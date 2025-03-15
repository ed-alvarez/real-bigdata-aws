""" Class for Processing downloaded Slack data from slack_data """

import json
import logging
import operator
import os
from datetime import datetime, timezone
from pprint import pprint
from typing import List, Optional, Tuple

import aws_lambda_context
import botocore.exceptions
import es_schema.es_slack_index as ess
import helpers.attachments
import helpers.es
import helpers.es_bulk_uploader
import helpers.es_slack_id
import helpers.file_io
import helpers.fingerprint_db
import helpers.s3
import helpers.utils
import helpers.utils as ut
import settings
import settings as sett
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

log = logging.getLogger()

sample_event = {
    "channels": None,
    "date_y_m_d": "2020-12-22",
    "client_name": "ips",
    "messages_s3_paths": [
        "dev.todo.slack/2020-12-22/json-slack/messages/C01FHG8T7J5__slack-ingest/2020-12-22.json",
        "dev.todo.slack/2020-12-22/json-slack/messages/G01FQMA8UVA__mpdm-anthony--james--mike-1/2020-12-22.json",
        "dev.todo.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json",
    ],
    "users": None,
}


def process_slack_from_lambda_event(event: dict, context: aws_lambda_context.LambdaContext = None):
    """Main entry method from e.g. lambda handler"""
    messages_s3_paths = event["messages_s3_paths"] if "messages_s3_paths" in event else []
    sp = SlackProcessor(
        event["client_name"],
        event["date_y_m_d"],
        messages_s3_paths,
        aws_lambda_context=context,
    )
    if "continue" in event and event["continue"] is True:
        return sp.process(
            continue_from_channel_id=event["continue_from_channel_id"],
            continue_from_item_num=event["continue_from_item_num"],
            continue_from_msg_num=event["continue_from_msg_num"],
        )
    return sp.process()


# Can use the return data struct from slack download too.
process_slack_from_slack_download_result = process_slack_from_lambda_event


def _get_sentiment(text: str) -> dict:
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)


# key = C00001__chname/20210216.json, label = C00001__chname, id = C00001, name = chname


def _try_get_s3_path_msgs(s3_path: str, s3_helper: helpers.s3.S3, continue_from_channel_id: Optional[str]) -> Tuple[str, bool]:
    # Method wrapping the error checking part of retrieving the messages from s3 as .process is
    # getting complex.
    _continue = False  # Flag to tell outer loop whether to continue or not.
    messages = ""
    try:
        messages = s3_helper.get(s3_path)
    except botocore.exceptions.ClientError as ex:
        if ex.response["Error"]["Code"] == "NoSuchKey":
            if continue_from_channel_id is None:
                log.warning(f"Key {s3_path} not found on s3, has it been processed already?")
                _continue = True
            else:
                log.error(f"Key {s3_path} not found on S3, but continue conversation was specified {continue_from_channel_id}")
                raise ex
        else:
            raise ex
    return messages, _continue


def _get_channel_label_from_msg_key(msg_key: str) -> str:
    return msg_key.split("/")[-2]


def _get_channel_id_from_msg_key(msg_key: str):
    """Get the channel id from an S3 key for a messages file"""
    channel_component = _get_channel_label_from_msg_key(msg_key)
    return channel_component.rsplit("__")[0]


def _get_channel_name_from_msg_key(msg_key: str):
    channel_component = _get_channel_label_from_msg_key(msg_key)
    return channel_component.rsplit("__")[1] if "__" in msg_key else ""


def _persist_data(
    es_bulk_uploader: helpers.es_bulk_uploader.ESBulkUploader,
    s3_helper: helpers.s3.S3,
    channel_es_documents: List[ess.SlackDocument],
    channel_label: str,
    date_y_m_d: str,
    start_msg_num: int,
    end_msg_num: int,
):
    # Method to write data to disk, S3 and Elasticsearch as well as remove unneeded files.
    channel_es_dicts = es_bulk_uploader.upload_docs(channel_es_documents)

    processed_local_path = os.path.join(
        settings.TEMPDIR,
        s3_helper.client_name,
        "processed",
        "messages",
        channel_label,
        f"{date_y_m_d}__{start_msg_num}-{end_msg_num}.json",
    )

    helpers.file_io.save_data_to_path(channel_es_dicts, processed_local_path)

    # Save processed json from local path to processed and archived folder
    s3_processed_path = s3_helper.upload_msg_json_to_s3_processed_subfolder(channel_label, processed_local_path)
    s3_helper.copy_file_from_processed_to_archived(s3_processed_path)


class SlackProcessor:
    def __init__(
        self,
        client_name: str,
        date_y_m_d: str,
        messages_s3_paths: list = None,  # None means get messages from archived folder
        aws_lambda_context: aws_lambda_context.LambdaContext = None,
    ):
        """Either take in a event dictionary (see sample above) or client name and date to process"""

        self.client_name = client_name
        self.date_y_m_d = date_y_m_d
        channels, users, is_future_metadata = helpers.s3.get_closest_metadata(client_name, date_y_m_d)
        if messages_s3_paths:
            self.messages_s3_paths = messages_s3_paths
        else:
            self.messages_s3_paths = helpers.s3.get_messages_for_date_from_archive(client_name, date_y_m_d)

        self.channels, self.users = channels, users
        self.aws_lambda_context = aws_lambda_context
        self.slack_api_token = settings.try_get_slack_api_token(client_name)

    def get_remaining_time_secs(self):
        if self.aws_lambda_context is not None:  # In Lambda
            return self.aws_lambda_context.get_remaining_time_in_millis() / 1000.0
        else:  # Not on Lambda
            return 999999999999

    def process(
        self,
        continue_from_channel_id: str = None,
        continue_from_msg_num: int = 0,
        continue_from_item_num: int = 0,
    ) -> dict:  # item_num includes attachments and messages.
        s3_helper = helpers.s3.S3(client_name=self.client_name, date_y_m_d=self.date_y_m_d)
        es_bulk_uploader = helpers.es_bulk_uploader.ESBulkUploader()
        num_messages = 0

        # Set up variables for es slack_id inner doc generator which takes care of memoization
        #       fingerprintdb_users_dict = (
        #           helpers.fingerprint_db.get_fingerprint_users_for_client(self.client_name)
        #       )

        fingerprintdb_users_dict = {}

        es_slack_id_inner_doc_creator = helpers.es_slack_id.SlackIdInnerDocCreator(
            self.client_name, fingerprintdb_users_dict, self.users
        )
        for s3_path in self.messages_s3_paths:
            channel_id = _get_channel_id_from_msg_key(s3_path)
            channel_name = _get_channel_name_from_msg_key(s3_path)
            channel_label = _get_channel_label_from_msg_key(s3_path)

            # If continue_from_channel_id is supplied and not None, search for that channel to start from
            if continue_from_channel_id is not None:
                if channel_id != continue_from_channel_id:
                    continue

            messages_out = []
            channel_es_documents = []
            # item number tracks messages AND attachments and serves as item id in ES
            channel_item_number = continue_from_item_num
            # message number tracks number of messages in downloaded list processed
            channel_message_number = continue_from_msg_num
            # Keep track of from and to message num for output filename when batching
            start_msg_num = continue_from_item_num
            end_msg_num = continue_from_item_num - 1

            messages_str, _continue = _try_get_s3_path_msgs(s3_path, s3_helper, continue_from_channel_id)
            if _continue:
                continue

            messages = json.loads(messages_str)
            # Time order messages by timestamp
            messages = sorted(messages, key=operator.itemgetter("ts"))

            is_todo = helpers.s3.is_todo_path(s3_path)
            attachment_file_ids = []  # TODO Remove  # Store processed attachments and move from _todo to processed at end if necessary

            raw_channel = self.channels.get(channel_id)
            if not raw_channel:
                log.error(f"Cannot find channelID {channel_id} so going to next")
                continue

            raw_channel_members = raw_channel.get("members")
            if not raw_channel_members:
                log.error(f"error with channel {channel_id}: No users found setting to unknown user")
                raw_channel_members = ["Unknown Channel Member"]
                pass

            channel_members = set(raw_channel_members)

            # Keep track of messages processed to pass to
            for m in messages[continue_from_msg_num:]:

                message = {}
                if "subtype" in m and m["subtype"] == "message_changed":
                    dt = ut.ts2datetime(m["ts"]).strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        m = m["message"]
                        m["text"] = f'Message from {dt} ({m["ts"]}) Changed: {m["text"]}'
                    except Exception as ex:
                        log.error(f"Message Changed Error so IGNORING changed essage : {m}")
                        log.error(ex)
                        continue

                # Bot messages have own structure dependent on bot
                if "subtype" in m and m["subtype"] == "bot_message":
                    continue

                message["from"] = m["user"]
                message["text"] = m["text"]
                message["ts"] = m["ts"]
                if "thread_ts" in m:
                    message["thread_ts"] = m["thread_ts"]
                message["datetime"] = datetime.fromtimestamp(float(m["ts"]))
                message["datetimeutc"] = datetime.utcfromtimestamp(float(m["ts"]))
                message["sentiment"] = _get_sentiment(m["text"])
                # Remove sender from to list unless user is alone.
                if len(channel_members) == 1:
                    message["to"] = channel_members
                else:
                    message["to"] = {cm for cm in channel_members if cm != m["user"]}
                message["to_channel_id"] = channel_id
                message["to_channel_name"] = channel_name

                this_sd = helpers.es.create_es_slack_document(
                    message,
                    self.client_name,
                    s3_helper,
                    channel_item_number,
                    channel_id,
                    channel_label,
                    self.channels,
                    self.users,
                    es_slack_id_inner_doc_creator,
                )

                pprint(message)
                messages_out.append(message)
                channel_es_documents.append(this_sd)
                channel_item_number += 1
                channel_message_number += 1
                num_messages += 1
                # end_msg_num needs to be pre-Increment
                end_msg_num += 1

                if "files" in m:
                    for file in m["files"]:
                        if "name" in file:
                            (text, error, processed_s3_path,) = helpers.attachments.get_attachment_data(
                                self.client_name,
                                self.date_y_m_d,
                                file["id"],
                                file["name"],
                                file["created"],
                                is_todo,
                                file["url_private_download"],
                                self.slack_api_token,
                            )
                        else:
                            # File has been tombstoned or made unavailable somehow
                            text = "File not available from Slack"
                            error = "File not available from Slack"
                            processed_s3_path = ""

                        attachment_file_ids.append(file["id"])  # TODO remove
                        filename = file["name"] if "name" in file else file["id"]
                        filesize = file["size"] if "size" in file else 0

                        attachment_slack_doc = helpers.es.create_es_attachment_slack_document(
                            file["id"],
                            filename,
                            filesize,
                            text,
                            error,
                            processed_s3_path,
                            message,
                            self.client_name,
                            s3_helper,
                            channel_item_number,
                            channel_id,
                            channel_label,
                            self.channels,
                            self.users,
                            es_slack_id_inner_doc_creator,
                        )
                        channel_es_documents.append(attachment_slack_doc)
                        channel_item_number += 1
                        num_messages += 1
                        end_msg_num += 1

                """ Check to see if flush requirements met (i.e. num of messages, memory of messages,
                execution time remaining then flush """
                lambda_no_time_left = self.get_remaining_time_secs() <= sett.LAMBDA_MIN_TIME_REQUIRED_SECS
                need_to_flush_data = (
                    len(channel_es_documents) >= sett.ES_UPLOAD_BATCH_SIZE
                    or ut.size_of_mb(channel_es_documents) >= sett.ES_UPLOAD_MAX_SIZE_MB
                    or lambda_no_time_left
                )
                print("lambda_no_time_left, self.get_execution_time_remaining_secs(), " "settings.LAMBDA_MIN_TIME_REQUIRED_SECS")
                print(
                    lambda_no_time_left,
                    self.get_remaining_time_secs(),
                    sett.LAMBDA_MIN_TIME_REQUIRED_SECS,
                )
                if need_to_flush_data:
                    # DEBUG
                    print("batch_number_exceeded, batch_mem_exceeded, lambda_no_time")
                    print(
                        len(channel_es_documents) >= sett.ES_UPLOAD_BATCH_SIZE,
                        ut.size_of_mb(channel_es_documents) >= sett.ES_UPLOAD_MAX_SIZE_MB,
                        lambda_no_time_left,
                    )
                    print("start msg num, end msg num")
                    print(start_msg_num, end_msg_num)
                    print("es docs size, ES_UPLOAD_MAX_SIZE_MB")
                    print(ut.size_of_mb(channel_es_documents), sett.ES_UPLOAD_MAX_SIZE_MB)

                if need_to_flush_data:
                    _persist_data(
                        es_bulk_uploader,
                        s3_helper,
                        channel_es_documents,
                        channel_label,
                        self.date_y_m_d,
                        start_msg_num,
                        end_msg_num,
                    )
                    channel_es_documents = []
                    attachment_file_ids = []  # TODO remove
                    start_msg_num = end_msg_num + 1

                """ Check to see if time remaining is less than limit, if so, return with continuation
                parameters to allow function/lambda to be called again. """
                if lambda_no_time_left:
                    return {
                        "ok": True,
                        "continue": True,
                        "continue_from_channel_id": channel_id,
                        "continue_from_msg_num": channel_message_number,
                        "continue_from_item_num": channel_item_number,
                        "num_messages_processed": num_messages,
                        "client_name": self.client_name,
                        "date_y_m_d": self.date_y_m_d,
                        "messages_s3_paths": self.messages_s3_paths,
                    }

            """
            Save messages to ES and S3 files. Do channel by channel so that processor can be re-run & process todo files
            in steps with each re-run. Otherwise re-running will always lead to failure to process all files
            """
            if end_msg_num >= start_msg_num:
                _persist_data(
                    es_bulk_uploader,
                    s3_helper,
                    channel_es_documents,
                    channel_label,
                    self.date_y_m_d,
                    start_msg_num,
                    end_msg_num,
                )

            # Processing for channel complete:
            # Move/copy message files to processed dir as per spec
            if is_todo:
                s3_helper.move_file_from_todo_to_processed(s3_path)
            else:
                s3_helper.copy_file_from_archived_to_processed(s3_path)

            # Blank out continue information for subsequent loops (used for first loop only)
            continue_from_channel_id = None
            continue_from_msg_num = 0
            continue_from_item_num = 0

        return {
            "ok": True,
            "continue": False,
            "num_messages_processed": num_messages,
            "client_name": self.client_name,
            "date_y_m_d": self.date_y_m_d,
        }
