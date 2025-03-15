import logging
from datetime import datetime
from io import BytesIO
from typing import Tuple
from zipfile import ZIP_DEFLATED, ZipFile

from teams_settings import FILE_STORE, Write_User_Data_To_File, processingStage
from teams_src.teams_shared_modules import paths_helper_functions
from teams_src.teams_shared_modules.file_handling import FileHandling

log = logging.getLogger()


def save_item_archive_to_disk(client: str, date_time: datetime, attachment_data: BytesIO, file_archive_name: str) -> str:
    file_store: FileHandling = FileHandling(FILE_STORE)
    saved_file_name = ""
    if attachment_data:
        if Write_User_Data_To_File:
            file_extension = ".zip"
            saved_file_name = paths_helper_functions.generate_processing_stage_file_path(
                name=file_archive_name,
                date=date_time,
                teams_processing_stage=processingStage.processed,
                file_ext=file_extension,
            )
            file_store: FileHandling = FileHandling.get(FILE_STORE)(file_name=saved_file_name, client=client)

            file_store.save_item_to_store(attachment_data.getvalue())

    else:
        log.warning(f"No item for archive")

    return saved_file_name


def _create_zip_archive() -> Tuple[ZipFile, BytesIO]:
    log.debug("Creating Archive file")
    zip_bytes_io = BytesIO()
    zip_archive = ZipFile(zip_bytes_io, mode="a", compression=ZIP_DEFLATED)
    return (zip_archive, zip_bytes_io)


def add_file_to_zip_archive(file_name: str, file_content: bytes) -> BytesIO:
    log.debug(f"Adding {file_name} to zip file")
    zip_archive: ZipFile
    zip_bytes_io: BytesIO
    zip_archive, zip_bytes_io = _create_zip_archive()
    try:
        zip_archive.writestr(file_name, data=file_content)
    except Exception as ex:
        log.exception(f"something wrong with Zipping archive file {file_name}")
    return zip_bytes_io
