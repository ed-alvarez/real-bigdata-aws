import logging
from datetime import datetime
from io import BytesIO

from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    zip_and_file_helper_functions,
)
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds
from teams_src.teams_shared_modules.teams_rest_api.teams_endpoint import TeamsEndpoint

log = logging.getLogger()


def add_attachment_to_zip_file(client: str, zip_file_name: str, file_name: str, content: bytes, date_time: datetime) -> str:
    archive_file_name = ""
    zip_attachment_file: BytesIO = zip_and_file_helper_functions.add_file_to_zip_archive(file_name=file_name, file_content=content)
    archive_file_name = zip_and_file_helper_functions.save_item_archive_to_disk(
        client=client,
        date_time=date_time,
        attachment_data=zip_attachment_file,
        file_archive_name=zip_file_name,
    )
    return archive_file_name


def get_attachment_data(url: str, client_creds: ClientCreds) -> bytes:
    endpoint_obj: TeamsEndpoint = TeamsEndpoint(clientCreds=client_creds)
    filedata: bytes = endpoint_obj.get_file(file_url=url)
    return filedata


def is_attachment_a_url_link(attachment: dict) -> bool:
    is_attachment_a_url_link: bool = False
    if attachment.get("contentType") == "reference":
        is_attachment_a_url_link = True
    return is_attachment_a_url_link
