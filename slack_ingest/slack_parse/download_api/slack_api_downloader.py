import logging
import ssl as ssl_lib
import time
from datetime import datetime, timedelta
from typing import Dict, List

import aws_lambda_context
import certifi
import ciso8601
import helpers.file_io
import helpers.s3
import helpers.utils
import settings
import slack
import slack.errors as slack_err
import slack_parse.ingest_helpers.slack_download_common as dl_common

log = logging.getLogger()


def download_slack_from_lambda_event(event: dict, context: aws_lambda_context.LambdaContext) -> Dict:
    """Main entry point from external caller e.g. lambda handler"""
    date_y_m_d = event["date_y_m_d"] if "date_y_m_d" in event else None
    force = event["force"] if "force" in event else False
    sd = SlackData(event["client_name"])
    return sd.download_all_data(date_y_m_d, force=force)


def _is_channel_in_existing_downloads(channel_id: str, existing_todo_paths: List[str]) -> bool:
    # e.g. 'dev.todo_.slack/2021-01-21/json-slack/messages/C01FHG8T7J5__slack-ingest/2021-01-21.json'
    for path in existing_todo_paths:
        channel_part = path.split("/")[-2].split("__")[0]
        if channel_part == channel_id:
            return True
    return False


# Turn date into seconds timestamp format (e.g. 1571321692.001200) for Slack
def ymd2ts(date_str="2019-11-01"):
    t = date_str
    ts = ciso8601.parse_datetime(t)
    # to get time in seconds:
    return str(time.mktime(ts.timetuple()))


def _get_informative_error_msg_from_slack_api_error(ex: slack_err.SlackApiError):
    if ex.response.data["error"] == "missing_scope":
        needed = ex.response.data["needed"]
        provided = ex.response.data["provided"]
        error_msg = "Missing Permission - Permission required = " + needed + "  Current permissions = " + provided
    else:
        error_msg = ex.response.data["error"]
    return error_msg


class SlackData:
    """This class controls the ingest and archive of Slack data on a time span basis"""

    def __init__(self, client_name: str):
        # Init slack client
        self.client_name = client_name
        self.ssl_context = None
        self.slack_client = None

        self.slack_api_token = settings.get_slack_api_token(client_name)

        self.ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
        self.slack_client = slack.WebClient(token=self.slack_api_token, ssl=self.ssl_context)

        self.try_connect_to_slack()

    def try_connect_to_slack(self):
        """Connect to Slack using the REST API"""
        log.info("Connecting to Slack")
        try:
            response = self.slack_client.auth_test()
        except slack_err.SlackApiError as ex:
            error_msg = ex.response.data["error"]
            log.error(error_msg)
            raise Exception(error_msg)

        return response

    def get_users(self, cursor=None, users=None):
        """Call Slack API to get complete list of users using pagination if
        necessary, hence recursive"""
        if users is None:
            users = []

        try:
            response = self.slack_client.users_list(cursor=cursor, limit=settings.SLACK_API_LIMIT_SIZE)
        except slack_err.SlackApiError as ex:
            error_msg = _get_informative_error_msg_from_slack_api_error(ex)  # will extract permissions based errors
            log.error(error_msg)
            raise Exception(error_msg)

        users += response["members"]

        if (next_cursor := response["response_metadata"]["next_cursor"]) != "":
            return self.get_users(cursor=next_cursor, users=users)
        return users

    def get_conversations_members(self, channel, cursor=None, members=None):
        members = members or []
        # TODO channel members = 0 returns error
        try:
            response = self.slack_client.conversations_members(channel=channel, cursor=cursor, limit=settings.SLACK_API_LIMIT_SIZE)
        except slack_err.SlackApiError as sae:
            print(sae.response["error"])
            if sae.response["error"] == "fetch_members_failed":  # Ex occurs if no members in channel.
                return []

        members += response["members"]

        if (next_cursor := response["response_metadata"]["next_cursor"]) != "":
            return self.get_conversations_members(channel=channel, cursor=next_cursor, members=members)
        return members

    def get_conversations_list(self, cursor=None, conversations=None):
        if conversations is None:
            conversations = []

        try:
            log.debug("Get conversation lists")
            response = self.slack_client.conversations_list(
                types="public_channel,private_channel,mpim,im",
                cursor=cursor,
                limit=settings.SLACK_API_LIMIT_SIZE,
            )
            from pprint import pprint

            pprint(response["channels"])
        except slack_err.SlackApiError as ex:
            error_msg = _get_informative_error_msg_from_slack_api_error(ex)  # will extract permissions based errors
            log.error(error_msg)
            raise Exception(error_msg)

        conversations += response["channels"]
        if (next_cursor := response["response_metadata"]["next_cursor"]) != "":
            return self.get_conversations_list(cursor=next_cursor, conversations=conversations)
        return conversations

    def get_conversations_lists_with_members(self):
        conversations = self.get_conversations_list()
        for conversation in conversations:
            conversation["members"] = self.get_conversations_members(channel=conversation["id"])
        return conversations

    def get_threaded_replies(self, channel, thread_ts, oldest, latest, messages=None, cursor=None):
        if messages is None:
            messages = []

        response = self.slack_client.conversations_replies(
            channel=channel,
            ts=thread_ts,
            oldest=oldest,
            latest=latest,
            cursor=cursor,
            limit=settings.SLACK_API_LIMIT_SIZE,
        )

        # For some reason parent messages also returned and for each cursor call, filter
        messages += [m for m in response["messages"] if m["ts"] != m["thread_ts"]]

        if response["has_more"] and (next_cursor := response["response_metadata"]["next_cursor"]) != "":
            return self.get_threaded_replies(
                channel=channel,
                thread_ts=thread_ts,
                oldest=oldest,
                latest=latest,
                messages=messages,
                cursor=next_cursor,
            )
        return messages

    def get_messages(self, channel, oldest, latest, messages=None, cursor=None):
        if messages is None:  # Default value of [] results in list being reused between method invocations
            messages = []

        # e.g. oldest = '2020-10-15T24:00:00'
        #      latest = '2020-12-12T00:00:00'
        if "-" in oldest:
            oldest = ymd2ts(oldest)
        if "-" in latest:
            latest = ymd2ts(latest)

        response = self.slack_client.conversations_history(
            channel=channel,
            oldest=oldest,
            latest=latest,
            cursor=cursor,
            limit=settings.SLACK_API_LIMIT_SIZE,
        )

        these_messages = response["messages"]
        messages += these_messages

        # Go through and fetch thread replies and add to messages list
        thread_replies = []

        for m in these_messages:  # messages is full list carried through recursion!
            these_replies = []

            if "thread_ts" in m and m["thread_ts"] == m["ts"]:  # i.e. is a thread parent
                these_replies = self.get_threaded_replies(
                    channel=channel,
                    thread_ts=m["thread_ts"],
                    oldest=oldest,
                    latest=latest,
                )
            thread_replies += these_replies

        messages += thread_replies
        # print('response_metadata' in response) <-- don't do this, seems to destroy response object

        if response["has_more"] and (next_cursor := response["response_metadata"]["next_cursor"]) != "":
            return self.get_messages(
                channel=channel,
                oldest=oldest,
                latest=latest,
                cursor=next_cursor,
                messages=messages,
            )
        return messages

    def download_all_data(self, date_y_m_d: str = None, force=False):
        today_y_m_d = datetime.now().strftime("%Y-%m-%d")
        if date_y_m_d:
            oldest = f"{date_y_m_d}T00:00:00"
            latest = f"{date_y_m_d}T24:00:00"
        else:
            yesterday = datetime.now() - timedelta(days=2)
            oldest = yesterday.strftime("%Y-%m-%dT00:00:00")
            latest = yesterday.strftime("%Y-%m-%dT24:00:00")

        # Prepare output result object
        results: dict = {
            "client_name": self.client_name,
            "date_y_m_d": oldest[0:10],
        }  # Y-m-d

        channels = self.get_conversations_lists_with_members()
        users = self.get_users()

        # Save locally and upload to S3 if no existing file for today
        channels_s3_path = dl_common.archive_data(self.client_name, data=channels, type_="channels", date_y_m_d=today_y_m_d)
        users_s3_path = dl_common.archive_data(self.client_name, data=users, type_="users", date_y_m_d=today_y_m_d)

        results["channels"] = channels_s3_path
        results["users"] = users_s3_path

        s3 = helpers.s3.S3(client_name=self.client_name, date_y_m_d=oldest[0:10])
        existing_todo_paths = s3.get_messages_paths_from_todo()
        results["messages_s3_paths"] = existing_todo_paths

        # Save and upload channels, download attachments for channels
        for channel in channels:
            if _is_channel_in_existing_downloads(channel["id"], existing_todo_paths) and not force:
                # channel has already been downloaded, move on to next
                print(f"channel {channel} has already been downloaded, skipping\n\n\n")
                continue
            messages = self.get_messages(channel=channel["id"], oldest=oldest, latest=latest)

            # TODO DELETE
            # for m in messages:
            #     if 'files' in m:
            #         attachment_file_paths = self.download_attachments(m)
            #         s3.upload_files_to_s3_todo_and_archived_subfolder(attachment_file_paths, 'attachments')

            if len(messages) > 0:
                channel_name = channel["name"] if "name" in channel else None
                this_s3_path = dl_common.archive_data(
                    self.client_name,
                    data=messages,
                    type_="messages",
                    channel_id=channel["id"],
                    channel_name=channel_name,
                    date_y_m_d=oldest[0:10],
                )
                results["messages_s3_paths"].append(this_s3_path)
        return results

    def retrieve_conversations(self):  # TODO DELETE
        """Iterate over each channel and retrieve a list of messages in the time range specified from the
        Slack REST API"""
        log.info("Iterate channels")
        for channel in self.slack_channels["channels"]:
            log.debug(f"Channel = {channel}")
            messages = self.paginate_messages(channel=channel["id"], latest=self.latest_ts, oldest=self.oldest_ts)

            num_mess = len(messages.data["messages"])
            if num_mess > 0:
                log.info(f"{num_mess} messages to process")
                self.process_messages_in_conversation(channel=channel, messages=messages)
            else:
                log.info(f"0 messages to process")

    def process_messages_in_conversation(self, channel, messages):  # TODO DELETE
        """Perform Archive and Ingest actions on each Message List"""
        log.info(f"Iterate messages")
        self.archive_conversation(channel=channel, messages=messages)
        self.process_for_ingest(messages=messages)

    def archive_conversation(self, channel, messages):  # TODO DELETE
        """Archive the Messages to the relevant JSON file"""
        log.info(f"Archive messages")

        if "name" in channel:
            channel_name = f"{channel['id']}_{channel['name']}"
        else:
            channel_name = f"{channel['id']}"

        try:
            conversation_archive = ArchiveData(
                json_obj=messages.data["messages"],
                template=settings.CHANNEL_HISTORY_FILE,
                channel_name=channel_name,
                file_date=ts2datetime(messages.data["oldest"]),
            )
        except KeyError as ex:
            error_msg = ex
            log.error(error_msg)
            pass

        conversation_archive.write_JSON_file()

    def process_for_ingest(self, messages):  # TODO DELETE
        """Format & ingest messages to ElasticSearch cluster"""
        log.info(f"Process messages for ingest")
        for message in messages.data["messages"]:

            if self.process_msg(message=message):
                msg = dict()
                msg["message"] = message["text"]
                msg["from_"] = self.user_dict[message["user"]]
                msg["to"] = ""
                msg["attachments"] = ""

            print(message)

    # '1571321692.001200'
    # '1571216377.000400'


if __name__ == "__main__":
    sd = SlackData("ips")
    sd.download_all_data("2021-01-13")

    # TODO DELETE
    @patch("slack.WebClient.conversations_history")
    def test_paginate_messages(mock_history):
        mock_history.side_effect = conversations_history
        slack_data = ParseSlack()
        slack_data.connect_to_slack()
        latest_ts = "2019-10-15T24:00:00"
        oldest_ts = "2019-10-15T00:00:00"
        slack_data.paginate_messages(channel="test", latest=latest_ts, oldest=oldest_ts)

    test_paginate_messages()

    latest_ts = "2019-10-15T24:00:00"
    oldest_ts = "2019-10-15T00:00:00"
    slack_data = ParseSlack()
    slack_data.set_dates(start_ts=oldest_ts, end_ts=latest_ts)
    slack_data.connect_to_slack()
    slack_data.retrieve_users()
    slack_data.retrieve_conversation_lists()
    slack_data.iterate_conversations()
