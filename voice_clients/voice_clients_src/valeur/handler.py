import logging
from typing import Dict, List

import aws_lambda_logging
from voice_clients_src.valeur import valeur_settings
from voice_clients_src.valeur.event_decode import EventDecode
from voice_clients_src.valeur.get_files_and_process import IterateDateList

log_level = valeur_settings.LOG_LEVEL
boto_log_level = valeur_settings.BOTO_LOG_LEVEL

log = logging.getLogger()


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")

    response = None

    try:
        log.debug("Start Valeur Voice Ingest")
        log.info(event)
        response = ingest_voice_calls(event, context)

        log.debug("End Valeur Voice Ingest")

    except Exception as error:
        response = {
            "status": 500,
            "error": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        log.exception(response)

    finally:
        event["response"] = response

        return {"message": f"{len(response)} Files copied successfully!", "event": event}


def ingest_voice_calls(event, context):
    """
    https://github.com/jetbridge/paramiko-lambda-layer
    goto sftp
    decrypt and copy files in previous period to S3 bucket (default period == day)

    kick off transcribe job for each file
    """

    """
    Decode Event
        Client : valeur
        Type : Daily/History
            Daily = yesterdays date for email files
                - Create a list with one date (yesterday)
            History requires a from-to = Date between which to ingest in form YYYY-MM-DD
                - Create a list of dates to process
    """

    event_decode: EventDecode = EventDecode(event=event)
    date_list: List = event_decode.DateList

    """
    Process Date list
        Iterate Dates from old to new
        sftp connect
        list files for date on sftp server
        Iterate files
            get audio file, decode & save to S3, (delete from sftp?)
                sftp_audio = 20210922-151637_1632316597.19842.wav.gpg
                s3_Audio = [client].ips/todo.voice/[yyyy-mm-dd]/[call_id].wav
            get CDR file, decode & save to s3 (delete from sftp?)
                sftp_cdr = 20210922-151637_1632316597.19842.json.gpg
                CDR = [client].ips/todo.voice/[yyyy-mm-dd]/[call_id].json
            start transcribe job
        sftp disconnect
    """
    process_date_list: IterateDateList = IterateDateList(client=event_decode.Client, date_list=date_list)
    list_of_s3_audio_files: List = process_date_list.process_list()

    result_list: List = []
    item: str
    for item in list_of_s3_audio_files:
        item_dict: Dict = {"key": item, "client": event_decode.Client}
        result_list.append(item_dict)

    return result_list
