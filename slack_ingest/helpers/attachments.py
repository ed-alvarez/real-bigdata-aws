"""
Attachments downloading and processing: supply client id, date and attachment id and the
get_text_from_attachment function will return the text for that file and clean up the downloaded and
extracted files.

Tika only for now. But there is filtering based on file extensions, which are specified in settings.py
"""

import io
import logging
import os
import re
import tarfile
import zipfile
from typing import Optional, Tuple

import helpers.s3
import helpers.utils
import requests
import settings
from tika import parser

log = logging.getLogger()


class NotSingleFileArchiveException(Exception):
    pass


class TikaParsingException(Exception):
    pass


TIKA_HEADERS = {
    "X-Tika-PDFextractInlineImages": "true",
    # 'Content-type': 'image/png', don't specify this, this breaks other attachments?
    "X-Tika-OCRLanguage": "eng",
}


def _parse_with_tika(full_path: str) -> Tuple[str, str]:
    try:
        tp = parser.from_file(full_path, headers=TIKA_HEADERS)
        # if tp['status'] == 200:
    except Exception as e:
        log.warning(e)
        return "", "Error parsing attachment"
    else:
        text = tp["content"] or ""
        text = re.sub(r"\n\s*\n", "\n\n", text)
    return text, ""


def _parse_with_tika_from_buffer(content: bytes) -> Tuple[str, str]:
    try:
        # tp = parser.from_file(full_path)
        tp = parser.from_buffer(content, headers=TIKA_HEADERS)
        # if tp['status'] == 200:
    except Exception as e:
        log.warning(e)
        return "", "Error parsing attachment."
    else:
        text = tp["content"] or ""
        text = re.sub(r"\n\s*\n", "\n\n", text)
    return text, ""


def _zipfile_dt_tuple(file_mtime: int) -> Tuple[int, int, int, int, int, int]:
    # turns a timestamp 16149320984 into dt tuple required for zipfile ZipInfo object
    dt = helpers.utils.ts2datetime(file_mtime)
    return dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second


def _to_zip(file_name: str, attachment_content: bytes, file_mtime: int) -> io.BytesIO:
    # NOTE: use this method with a "with" clause or explicitly call .close() on the result to
    # release the memory used to store the attachment
    # source = io.BytesIO(initial_bytes=attachment_content)  todo delete
    bytes_fh = io.BytesIO()
    with zipfile.ZipFile(bytes_fh, "a", zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo(file_name, _zipfile_dt_tuple(file_mtime))
        z.writestr(info, attachment_content)
    return bytes_fh


def _from_zip(zip_content: bytes) -> bytes:
    with io.BytesIO(initial_bytes=zip_content) as source:
        with zipfile.ZipFile(source, "r") as z:
            names = z.namelist()
            if len(names) != 1:
                raise NotSingleFileArchiveException
            file_content = z.read(names[0])
    return file_content


def _to_tgz(file_name: str, attachment_content: bytes, file_mtime: int) -> io.BytesIO:
    # NOTE: use this method with a "with" clause or explicitly call .close() on the result to
    # release the memory used to store the attachment
    source = io.BytesIO(initial_bytes=attachment_content)
    bytes_fh = io.BytesIO()
    with tarfile.open(fileobj=bytes_fh, mode="w:gz") as tf:
        info = tarfile.TarInfo(file_name)
        info.size = len(attachment_content)
        info.mtime = file_mtime
        tf.addfile(info, source)
    import helpers.utils

    print("\n\n\n\n debug 2 \n")
    print(helpers.utils.size_of_mb(bytes_fh))
    print(file_name)
    return bytes_fh


def _from_tgz(tgz_content: bytes) -> bytes:
    with io.BytesIO(initial_bytes=tgz_content) as source:
        with tarfile.open(fileobj=source, mode="r:gz") as tf:
            members = tf.getmembers()
            if len(members) != 1:
                raise NotSingleFileArchiveException
            ef = tf.extractfile(members[0].name)
            file_content = ef.read() if ef is not None else bytes([])
    return file_content


def _get_data_from_tmp_tar_attachment(path: str):
    # Extract file from tarfile and get filename

    archive_output_dir = os.path.join(settings.TEMPDIR, "attachments_processing")
    if path.lower().endswith(".tgz") or path.lower().endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as tf:
            members = tf.getmembers()
            if len(members) > 1:
                raise NotSingleFileArchiveException
            filename = members[0].name
            file_size = members[0].size
            extension = os.path.splitext(filename)[1][1:]  # slices don't error on empty strings/lists
            if extension.lower() in settings.ATTACHMENTS_IGNORE_LIST:
                info_msg = f"Attachment parsing skipped for: {filename} due to unsupported extension."
                log.info(info_msg)
                return filename, file_size, "", info_msg
            tf.extract(filename, archive_output_dir)
    else:
        with zipfile.ZipFile(path, "r") as z:
            infos = z.infolist()
            if len(infos) != 1:
                raise NotSingleFileArchiveException
            filename = infos[0].filename
            file_size = infos[0].file_size
            is_valid_attachment, error_str = _is_valid_attachment_type(filename)
            if not is_valid_attachment:
                return filename, 0, "", error_str
            z.extract(filename, archive_output_dir)

    # Parse with tika, etc
    try:
        full_path = os.path.join(archive_output_dir, filename)
        text, warn_msg = _parse_with_tika(full_path)
    except TikaParsingException as tpe:
        warn_msg = f"Error parsing with Tika: {tpe}"
        log.warning(warn_msg)
        text = ""

    finally:  # Clean up extracted file
        os.remove(os.path.join(archive_output_dir, filename))

    return filename, file_size, text, warn_msg


def download_attachment_from_slack(url: str, slack_api_token: str) -> Tuple[Optional[bytes], str]:
    if slack_api_token != "":  # nosec
        headers = {"Authorization": "Bearer %s" % slack_api_token}
    else:
        headers = {}  # Leave headers blank, token is in URL for slack export urls

    try:
        r = requests.get(url, headers=headers)
    except Exception as e:
        log.error(f"Could not download {url} because {e}")
        return None, "Error downloading"
    return r.content, ""

    """
        r = requests.get(url, headers=headers)
        with open(tmp_file_path, 'wb') as f:
            f.write(r.content)
        # lambda has 512 mb disk space at /tmp
        with tarfile.TarFile.open(tar_file_path, 'w:gz') as tf:
            tf.add(tmp_file_path, arcname=filename)
    os.unlink(tmp_file_path)  os.unlink(tmp_file_path)
    """


def _is_valid_attachment_type(file_name) -> Tuple[bool, str]:
    extension = os.path.splitext(file_name)[1][1:]  # slices don't error on empty strings/lists
    if extension.lower() in settings.ATTACHMENTS_IGNORE_LIST:
        info_msg = f"Attachment parsing skipped for: {file_name} due to unsupported extension."
        log.info(info_msg)
        return False, info_msg
    else:
        return True, ""


def get_attachment_data(  # nosec
    client_name: str,
    date_y_m_d: str,
    attachment_id: str,
    file_name: str,
    file_date: int,
    is_todo: bool = False,
    url: str = "",
    slack_api_token: str = "",
) -> Tuple[str, str, str]:

    s3 = helpers.s3.S3(client_name=client_name, date_y_m_d=date_y_m_d)
    processed_s3_path = s3.get_processed_s3_key_for_attachment(attachment_id)
    todo_s3_path = s3.get_todo_s3_key_for_attachment(attachment_id)
    archived_s3_path = s3.get_archived_s3_key_for_attachment(attachment_id)
    if is_todo:  # Download from slack using url and slack_api_token
        attachment_content, error = download_attachment_from_slack(url, slack_api_token)
        if attachment_content is None:
            return "", "Attachment was empty", ""
        if error:
            return "", error, ""

        # Upload file to S3 _todo and copy to archived folder.
        # Closing the _to_tgz fh ensures memory is released (checked with helpers.utils.size_of_mb)
        if settings.ARCHIVE_EXTENSION == "tgz" or settings.ARCHIVE_EXTENSION == "tar.gz":
            _to_archive = _to_tgz
        elif settings.ARCHIVE_EXTENSION == "zip":
            _to_archive = _to_zip

        with _to_archive(file_name, attachment_content, file_date) as attachment_archive:
            s3.put_file_object_to_key(attachment_archive.getvalue(), todo_s3_path)
        s3.copy_file_from_todo_to_archived(todo_s3_path)

        is_valid_attachment, error_text = _is_valid_attachment_type(file_name)
        if not is_valid_attachment:
            log.info(f"Attachment extension unparseable: {file_name}, in {archived_s3_path}")
            s3.move_file_from_todo_to_unprocessed(todo_s3_path)
            return "", error_text, archived_s3_path

        text, error_str = _parse_with_tika_from_buffer(attachment_content)
        s3.move_file_from_todo_to_processed(todo_s3_path)

        return text, error_str, processed_s3_path
    else:  # Load attachment from S3 don't need url or slack token
        archived_s3_path = s3.get_archived_s3_key_for_attachment(attachment_id)

        # Check if we need to download file at all
        is_valid_attachment, error_text = _is_valid_attachment_type(file_name)
        if not is_valid_attachment:
            return "", error_text, archived_s3_path

        archive_content = s3.get(archived_s3_path)
        if settings.ARCHIVE_EXTENSION == "tgz" or settings.ARCHIVE_EXTENSION == "tar.gz":
            _from_archive = _from_tgz
        elif settings.ARCHIVE_EXTENSION == "zip":
            # special case where we're actually using dynamic typing
            _from_archive = _from_zip  # type: ignore
        file_content = _from_archive(archive_content)

        text, error_str = _parse_with_tika_from_buffer(file_content)
        s3.copy_file_from_archived_to_processed(archived_s3_path)
        return text, error_str, archived_s3_path

        # # Previous method (download file locally to tmp)
        # archived_s3_path = s3.get_archived_s3_key_for_attachment(attachment_id)
        # tar_file_path = s3.download_attachment_to_tmp(attachment_id, is_todo)
        # file_name, file_size, text, error = _get_data_from_tmp_tar_attachment(tar_file_path)

        # # Cleanup downloaded tar file
        # os.remove(tar_file_path)
        # s3.copy_file_from_archived_to_processed(archived_s3_path)
    # return text, error, processed_s3_path
