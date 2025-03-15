"""
SFTP client class
"""
from io import BytesIO
from logging import getLogger
from math import ceil
from os import path
from stat import S_ISDIR, S_ISREG
from time import time
from typing import Dict, List

import boto3

from shared.shared_src import uncompress_file
from shared.shared_src.utils import timing

DOWNLOAD_S3_CHUNK_SIZE = 6291456

log = getLogger()


class SFTPClient:
    def __init__(self, sftp_connection, s3_connection=None):
        self._sftp_client = sftp_connection.sftp_client
        self._s3_connection = s3_connection or boto3.client("s3")
        self._directory_contents = ""
        self._remote_directory = ""

    @staticmethod
    def isdir(sftp, path):
        try:
            return S_ISDIR(sftp.stat(path).st_mode)
        except IOError:
            pass

    def get_file_line_items(self, filename):
        """Retrieve file and convert from a binary object to a string object"""
        log.debug(f"Processing {filename}")
        try:
            with self._sftp_client.open(filename, "rb") as sftp_f:
                with uncompress_file.uncompress_reader(readable=sftp_f, filename=filename) as f:
                    file_data = f.read()
            log.debug('{"File Data" : %s"}' % str(file_data))
            return [x.decode("utf-8") for x in file_data.splitlines()]
        except Exception as ex:
            log.error(f"Cannot retrieve : {filename} Error: {ex}")

    def _transfer_chunk_from_ftp_to_s3(
        self, ftp_file: bytes, s3_connection, multipart_upload: Dict, bucket_name, ftp_file_path, s3_file_path, part_number, chunk_size
    ):
        start_time: time = time()
        chunk = ftp_file.read(int(chunk_size))
        part = s3_connection.upload_part(
            Bucket=bucket_name,
            Key=s3_file_path,
            PartNumber=part_number,
            UploadId=multipart_upload["UploadId"],
            Body=chunk,
        )
        end_time: time = time()
        total_seconds = end_time - start_time
        log.info("speed is {} kb/s total seconds taken {}".format(ceil((int(chunk_size) / 1024) / total_seconds), total_seconds))
        part_output = {"PartNumber": part_number, "ETag": part["ETag"]}
        return part_output

    @timing
    def get_sftp_file(self, ftp_file_path: str) -> bytes:
        flo = BytesIO()
        self._sftp_client.getfo(ftp_file_path, flo)
        flo.seek(0)
        ftp_file_data: bytes = flo.read()
        return ftp_file_data

    def transfer_file_from_ftp_to_s3(self, bucket_name, ftp_file_path, s3_file_path, chunk_size=DOWNLOAD_S3_CHUNK_SIZE):
        ftp_connection = self._sftp_client
        ftp_file = ftp_connection.file(ftp_file_path, "r")
        s3_connection = self._s3_connection
        ftp_file_size = ftp_file._get_size()
        try:
            s3_file = s3_connection.head_object(Bucket=bucket_name, Key=s3_file_path)
            if s3_file["ContentLength"] == ftp_file_size:
                log.info("File Already Exists in S3 bucket")
                ftp_file.close()
                return
        except Exception as e:
            pass
        if ftp_file_size <= int(chunk_size):
            # upload file in one go
            log.info("Transferring complete File from FTP to S3...")
            ftp_file_data = ftp_file.read()
            s3_connection.upload_fileobj(ftp_file_data, bucket_name, s3_file_path)
            log.info("Successfully Transferred file from FTP to S3!")
            ftp_file.close()

        else:
            log.info("Transferring File from FTP to S3 in chunks...")
            # upload file in chunks
            chunk_count: int = int(ceil(ftp_file_size / float(chunk_size)))
            multipart_upload = s3_connection.create_multipart_upload(Bucket=bucket_name, Key=s3_file_path)
            parts: List = []
            i: int
            for i in range(chunk_count):
                log.info("Transferring chunk {}...".format(i + 1))
                part = self._transfer_chunk_from_ftp_to_s3(
                    ftp_file, s3_connection, multipart_upload, bucket_name, ftp_file_path, s3_file_path, i + 1, chunk_size
                )
                parts.append(part)
                log.info("Chunk {} Transferred Successfully!".format(i + 1))

            part_info: Dict = {"Parts": parts}
            s3_connection.complete_multipart_upload(
                Bucket=bucket_name, Key=s3_file_path, UploadId=multipart_upload["UploadId"], MultipartUpload=part_info
            )
            log.info("All chunks Transferred to S3 bucket! File Transfer successful!")
            ftp_file.close()

    def download_files_to_tmp(self, files_to_retrieve):
        local_files_list = []
        for remote_file in files_to_retrieve:
            try:
                local_path = "/tmp"
                local_file = path.join(local_path, path.basename(remote_file))
                local_files_list.append(local_file)

                log.info(f"SFTP from {remote_file} to {local_file}")
                self._sftp_client.get(remote_file, local_file)
            except Exception as e:
                log.error(f"Failed to GET Remote File : {remote_file} Error = {e}")
                raise
        return local_files_list

    def get_files_in_directory(self, remote_dir="."):
        try:
            self._directory_contents = self._sftp_client.listdir_attr(path=remote_dir)
        except Exception as e:
            err_msg = f"Failed to List Remote Directory : {remote_dir} Error = {e}"
            log.error(err_msg)
            raise
        self._remote_directory = remote_dir
        return self._directory_contents

    def list_files_in_directory(self, file_prefix="", remote_dir="."):
        files = []
        if self._remote_directory != remote_dir or not self._directory_contents:
            self.get_files_in_directory(remote_dir=remote_dir)

        for entry in self._directory_contents:
            mode = entry.st_mode
            if S_ISDIR(mode):
                log.debug(entry.filename + " is folder")
            elif S_ISREG(mode):
                log.debug(entry.filename + " is file")
                if entry.filename.startswith(file_prefix):
                    files.append(entry.filename)
        return files

    def list_of_files_containing(self, containing, remote_dir="."):
        files = []

        if self._remote_directory != remote_dir or not self._directory_contents:
            self.get_files_in_directory(remote_dir=remote_dir)

        for entry in self._directory_contents:
            mode = entry.st_mode
            if S_ISREG(mode):
                if containing in entry.filename:
                    files.append(entry.filename)
        return files


if __name__ == "__main__":
    from bbg_ingest.bbg_src.file_download_lambda.sftp_connection import SFTPConnection

    sftp_cobnnection = SFTPConnection(client_id="mc913915589", client_name="valeur")
    sftp_client = SFTPClient(sftp_cobnnection)
