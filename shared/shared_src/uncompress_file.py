from bz2 import BZ2File
from gzip import GzipFile
from io import BytesIO
from logging import getLogger
from os import path

log = getLogger()

extension_map = {
    ".bz2": BZ2File,
    ".gz": GzipFile,
}


def uncompress_reader(readable, filename):
    """Wrap file reader if files needs un-compressing"""
    try:

        _, extension = path.splitext(filename)
        opener = extension_map.get(extension)
        if opener:
            log.debug(f"It is a compressed file so Open filename {filename} with {opener}")
            file_content = None
            try:
                file_content = opener(fileobj=readable, filename=filename)
            except Exception as ex:
                log.debug(ex)
            return file_content
        else:
            log.debug(f"It is not a compressed file so pass though contents")
            return readable  # pass straight through
    except Exception as e:
        log.error(f"Failed to get reader for : {filename}. Error = {e}")
        raise


def uncompress_file(filename, file_content):
    dst_file, extension = path.splitext(filename)
    opener = extension_map.get(extension)
    if opener:
        file_obj = BytesIO(file_content)
        with opener(fileobj=file_obj, mode="rb") as f_in:
            contents = f_in.read()
        return dst_file, contents
    else:
        return filename, file_content
