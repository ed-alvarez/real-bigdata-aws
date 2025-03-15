from datetime import datetime
from io import BytesIO
from typing import List

from bs4 import BeautifulSoup
from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    zip_and_file_helper_functions,
)
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds, imageURL
from teams_src.teams_shared_modules.teams_rest_api.teams_endpoint import TeamsEndpoint


def add_images_to_zip_file(client: str, zip_file_name: str, file_name: str, content: bytes, date_time: datetime) -> str:
    image_file_name: str = ""
    zip_attachment_file: BytesIO = zip_and_file_helper_functions.add_file_to_zip_archive(file_name=file_name, file_content=content)
    image_file_name = zip_and_file_helper_functions.save_item_archive_to_disk(
        client=client,
        date_time=date_time,
        attachment_data=zip_attachment_file,
        file_archive_name=zip_file_name,
    )
    return image_file_name


def _extract_images_from_content(content: str) -> List[str]:
    result = []
    soup = BeautifulSoup(content, features="html.parser")
    imgs = soup.findAll("img")
    for img in imgs:
        img_url = img["src"]
        result.append(img_url)
    return result


def _get_image_data(url: str, client_creds: ClientCreds) -> bytes:
    endpoint_obj: TeamsEndpoint = TeamsEndpoint(clientCreds=client_creds)
    filedata: bytes = endpoint_obj.get_image(image_full_url=url)
    return filedata


def _decode_image_url(url: str) -> imageURL:
    url_payload: str = url.replace("https://graph.microsoft.com/beta/", "")
    url_parts: List = url_payload.split("/")
    chat_id: str = url_parts[1]
    message_id: str = url_parts[3]
    hosted_contents_id: str = url_parts[5]
    image_url: imageURL = imageURL(chat_id=chat_id, message_id=message_id, hosted_contents_id=hosted_contents_id)
    return image_url


def get_images(content: str, client_creds: ClientCreds) -> List[imageURL]:
    image_archive_files: List[imageURL] = []
    image_urls: List = _extract_images_from_content(content=content)
    for url in image_urls:
        image_data: imageURL = _decode_image_url(url=url)
        image_data.content = _get_image_data(url=url, client_creds=client_creds)
        image_archive_files.append(image_data)

    return image_archive_files
