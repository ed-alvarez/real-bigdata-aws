import base64
import logging
import tarfile
from io import BytesIO
from typing import List

log = logging.getLogger()


def xstr(s) -> str:
    """Function to convert to string and return a blank if the input is None"""
    return "" if s is None else str(s)


def match_file_name(list_of_files: List, original_file_name: str) -> str:
    files_lower: List = [item.lower() for item in list_of_files]
    try:
        position_matches: List = [i for i, elem in enumerate(files_lower) if original_file_name.lower() in elem]
        position: int = position_matches[0]
    except Exception as ex:
        log.exception(ex)
        log.warning(f"File {original_file_name} not found in file list {list_of_files}")
        return ""
    extract_tar_file: str = list_of_files[position] if position < len(list_of_files) else ""
    return extract_tar_file


def extract_file_from_tar(file_name_to_extract: str, tar_file_name: str, tar_file_contents: bytes) -> str:
    """
    Function to extract file_name_to_extract from TAR archive,
    encode it as B64 and return the results as a string
    or retun a blank string if file not found
    """
    log.debug(f"Extracting FILE {file_name_to_extract} from the TAR file {tar_file_name}")
    # Gather base file info for processing and check it is valid

    # Open the archive file using a context manager to manage cleanup
    # https://jeffknupp.com/blog/2016/03/07/python-with-context-managers/
    with tarfile.open(fileobj=BytesIO(tar_file_contents), mode="r:gz") as tar_file_archive:
        log.debug(f"Opened the TAR {tar_file_archive}")
        # loop around the members of the archive file.  A member can be a directory or a file
        files_in_archive: List = tar_file_archive.getnames()
        extract_tar_file = match_file_name(list_of_files=files_in_archive, original_file_name=file_name_to_extract)
        try:
            tar_file_archive.getmember(extract_tar_file)
            log.debug("Found the file in the Archive")
        except Exception as ex:
            log.exception(ex)
            log.warning(f"File {extract_tar_file} not found in TAR file {tar_file_name}")
            return ""

        archive_file = tar_file_archive.extractfile(extract_tar_file)
        encoded_file: bytes = base64.b64encode(archive_file.read())
        return_string: str = xstr(str(encoded_file, "utf-8"))

        log.debug(f"Extracted file from the archive")
        return return_string
