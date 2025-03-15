"""
Download files from Bloomberg

Expects 3 or 4 parameters

client_name = client name as used in aws buckets
bbg_client_id = the sftp_login client ID for bloomberg
bbg_manifest = DAILY or ARCHIVE
manifest_date = date of manifest = yymmdd format for manifest

Daily has 5 days worth of manifest then Archive has another 30 days after that

Downloads the Manifest from BBG to tmp then uploads from tmp to correct S3 bucket

Returns If sucessful
    client_name
    files_downloaded - List of files with s3 path
    files_decoded - empty holder for decode
    has_files = True

As using a datacalss any errors return as error = True

Returns if missing required files from manifest
    client_name
    error_msg: 'Not all files required by decode are available.  Missing [types]'


Returns if files listed in Manifest are NOT present on SFTP server
    client_name
    error_msg: 'Manifest files missing from sFTP: [missing files]'


Can error out if connection to s3 is broken

"""

import logging
import os
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from typing import List

from bbg_helpers.helper_dataclass import DownloadLambdaParameters
from bbg_settings import (
    BBG_ARCHIVE_MANIFEST,
    BBG_DAILY_MANIFEST,
    BOTO_LOG_LEVEL,
    LOG_LEVEL,
    S3_FOLDER_DOWNLOAD,
)
from bbg_src.file_download_lambda.sftp_client import SFTPClient
from bbg_src.file_download_lambda.sftp_connection import SFTPConnection

from shared.shared_src import uncompress_file, utils
from shared.shared_src.s3.s3_helper import S3Helper

log_level = LOG_LEVEL
boto_log_level = BOTO_LOG_LEVEL
log = logging.getLogger()


class FileDownloadException(Exception):
    pass


class BBGFileDownload:
    def __init__(self, event):
        self._event = event
        self._lambda_parameters = DownloadLambdaParameters(**self._event)
        self._s3_client: S3Helper = S3Helper(client_name=self._event["client_name"], ingest_type="bbg")
        self._sftp_connection = None
        self._sftp_client = None

    def set_up_sftp_connection(self):
        log.debug("Setup SFTP Connection")
        try:
            self._sftp_connection = SFTPConnection(
                client_name=self._lambda_parameters.client_name,
                client_id=self._lambda_parameters.bbg_client_id,
            )
        except Exception as ex:
            log.error(ex)
            raise FileDownloadException(ex)

    def connect_classes(self):
        self.set_up_sftp_connection()
        self._sftp_client = SFTPClient(self._sftp_connection)

    def remove_file_from_file_lists(self, list_of_files, parts_to_remove):
        new_file_list = []

        for file in list_of_files:
            if any(part in file for part in parts_to_remove):
                pass
            else:
                new_file_list.append(file)
        return new_file_list

    def get_full_file_from_partial_match(self, file_partial_match, list_of_files):
        for file in list_of_files:
            if file_partial_match in file:
                return file

    def generate_manifest_file_name(self):
        manifest_full_file_name = ""
        manifest_file_head = "daily_manifest"
        if self._lambda_parameters.manifest_date:
            # The final un archived manifest file is infact archived
            manifest_file_name = "_".join([manifest_file_head, f"{self._lambda_parameters.manifest_date}.txt"])

            # Get all the daily_manifest files
            files = self._sftp_client.list_files_in_directory(file_prefix=manifest_file_head)

            # clean any .html files from the list
            list_of_manifest_files = self.remove_file_from_file_lists(files, parts_to_remove=[".html", ".html.gz"])

            # Get the full name of the manifest file in case it has .gz on the end of it
            manifest_full_file_name = self.get_full_file_from_partial_match(
                file_partial_match=manifest_file_name, list_of_files=list_of_manifest_files
            )
        else:
            manifest_full_file_name = "_".join([manifest_file_head, "current.txt"])

        log.info(f"Generated {manifest_full_file_name} Manifest")
        return manifest_full_file_name

    def get_daily_manifest_list_of_files(self):
        manifest_full_file_name = self.generate_manifest_file_name()
        files_to_retrieve = self._sftp_client.get_file_line_items(manifest_full_file_name)
        log.info(f"List of files to retrieve {files_to_retrieve}")
        return files_to_retrieve

    def get_archive_manifest_list_of_files(self):
        log.debug(f"Processing Archive {self._lambda_parameters.manifest_date}")
        manifest = BBG_ARCHIVE_MANIFEST.format(yymmdd=self._lambda_parameters.manifest_date)
        log.debug(f"Manifest name = {manifest}")
        file_line_items: List = self._sftp_client.get_file_line_items(manifest)
        log.debug(f"File Line Items {file_line_items}")
        files_to_retrieve = [f"Archive/{x}.gz" for x in file_line_items]
        log.info(f"List of files to retrieve {files_to_retrieve}")
        return files_to_retrieve

    def get_manifest_file_parts_for_files_on_sftp_site(self, files_to_retrieve):
        files_out = defaultdict(list)
        for file in files_to_retrieve:
            part = file.split(".")
            if part[-1] == "gpg" or part[-2] == "gpg":
                if part[2] == "att":
                    bbg_part = f"{part[1]}.{part[2]}"
                else:
                    bbg_part = f"{part[1]}"
                files_out[part[0]].append(bbg_part)
        return files_out

    def get_list_of_files_from_manifest(self):
        files_to_retrieve = ""
        if self._lambda_parameters.bbg_manifest == "DAILY":
            log.debug("processing DAILY files")
            files_to_retrieve = self.get_daily_manifest_list_of_files()
        else:
            log.debug("processing ARCHIVE files")
            files_to_retrieve = self.get_archive_manifest_list_of_files()
        if not files_to_retrieve:
            raise ValueError(f"No files available for {self._lambda_parameters.bbg_manifest} {self._lambda_parameters.manifest_date}")

        return files_to_retrieve

    def get_list_of_files_from_sftp_server(self, file_date):
        files_to_retrieve = ""
        if self._lambda_parameters.bbg_manifest == "DAILY":
            raw_files_on_sftp_server = self._sftp_client.list_of_files_containing(containing=file_date)
        else:
            # self._sftp_client.get_files_in_directory(remote_dir='Archive')
            raw_files_on_sftp_server_archive = self._sftp_client.list_of_files_containing(containing=file_date, remote_dir="Archive")
            raw_files_on_sftp_server = [f"Archive/{x}" for x in raw_files_on_sftp_server_archive]

        # Clean the manifest file names out of the list
        list_of_files_on_sftp = self.remove_file_from_file_lists(raw_files_on_sftp_server, parts_to_remove=["html", "txt"])

        if not list_of_files_on_sftp:
            raise ValueError(
                f"No files available on SFTP server for {self._lambda_parameters.bbg_manifest} {self._lambda_parameters.manifest_date}"
            )

        return list_of_files_on_sftp

    def check_all_ips_required_files_are_on_sftp_site(self, files_to_retrieve):
        expected_types = ["msg", "ib19", "msg.att", "ib19.att"]
        missing_list = ""
        files_out = self.get_manifest_file_parts_for_files_on_sftp_site(files_to_retrieve)
        for account, file_types in files_out.items():
            missing_list = set(expected_types).difference(file_types)
            if len(missing_list) > 0:
                log.error(f'Files - {", ".join(missing_list)} are missing from {account} Bloomberg sFTP server')
                return missing_list
            else:
                log.info(f'All Files - {", ".join(expected_types)} are present on the {account} Bloomberg sFTP server')
                return missing_list

    def check_all_manifest_files_are_on_sftp_site(self, files_to_retrieve_from_manifest, files_to_retrieve_from_sftp):
        file_missing_from_sftp_site = []
        for manifest_file in files_to_retrieve_from_manifest:
            if any(sftp_file in manifest_file for sftp_file in files_to_retrieve_from_sftp):
                pass
            else:
                file_missing_from_sftp_site.append(manifest_file)
        return file_missing_from_sftp_site

    def remove_path_from_file_list(self, list_of_files):
        files_only = []
        for file in list_of_files:
            files_only.append(os.path.basename(file))
        return files_only

    def generate_wait_until(self):
        return str(datetime.utcnow().replace(hour=17, minute=0, second=0, microsecond=0).isoformat() + "Z")

    def generate_directory_prefix(file_name: str) -> str:
        directory_parts: List = file_name.split("/")
        directory_prefix: str = f"{directory_parts[0]}/{directory_parts[1]}/"
        return directory_prefix

    def file_download(self):
        log.debug("file_download {}".format(self._event))
        result = {}

        # Get manifest_file from Daily, Daily with date or Archive
        try:
            log.debug("retrieve files from manifest")
            files_to_retrieve_from_manifest = self.get_list_of_files_from_manifest()
        except Exception as ex:
            err_msg = f"Unable to parse Manifest File.  Error {ex}"
            log.error(err_msg)
            self._lambda_parameters.error = True
            self._lambda_parameters.error_msg = err_msg
            return asdict(self._lambda_parameters)

        # Get the file date to check for files on the server
        file_date = files_to_retrieve_from_manifest[0].split(".")[2]
        try:
            files_to_retrieve_from_sftp = self.get_list_of_files_from_sftp_server(file_date=file_date)
        except Exception as ex:
            err_msg = f"Unable to retrieve list of Files from the sFTP server.  Error {ex}"
            log.error(err_msg)
            self._lambda_parameters.error = True
            self._lambda_parameters.error_msg = err_msg
            return asdict(self._lambda_parameters)

        missing_files = self.check_all_manifest_files_are_on_sftp_site(files_to_retrieve_from_manifest, files_to_retrieve_from_sftp)
        if missing_files and not self._lambda_parameters.error:
            missing_files_txt = ",".join(missing_files)
            err_msg = f"Manifest files missing from sFTP: {missing_files_txt}"
            log.error(err_msg)
            self._lambda_parameters.error = True
            self._lambda_parameters.error_msg = err_msg
            self._lambda_parameters.wait_until = self.generate_wait_until()
            return asdict(self._lambda_parameters)

        # check all manifest files are actually on the sFTP site
        # there is a wait_until gate which will stop the error if the wait_until is present
        # the implication being that the error has been hit on the first time round, the wait has happened
        # and now its time to download & decode whatever is there
        ips_required_files = self.check_all_ips_required_files_are_on_sftp_site(files_to_retrieve_from_manifest)
        if not self._lambda_parameters.error and ips_required_files:
            missing_types_txt = ",".join(ips_required_files)
            err_msg = f"Not all files required by decode are available.  Missing {missing_types_txt}"
            log.error(err_msg)
            self._lambda_parameters.error = True
            self._lambda_parameters.error_msg = err_msg
            self._lambda_parameters.wait_until = self.generate_wait_until()
            return asdict(self._lambda_parameters)

        formatted_file_date: str = utils.get_date_from_file_path(files_to_retrieve_from_manifest[0])
        self._s3_client.directoryDate = formatted_file_date

        s3_file_list: List = []
        for sftp_file in files_to_retrieve_from_sftp:
            # Download files from BBG SFTP to the local TMP directory and gunzip if neccessary
            try:
                log.info(f"Getting data file {sftp_file} from Bloomberg")
                ftp_file_data: bytes = self._sftp_client.get_sftp_file(sftp_file)
            except Exception as ex:
                err_msg = f"Unable to get file from sftp Server.  Error {ex}"
                log.exception(err_msg)
                self._lambda_parameters.error = True
                self._lambda_parameters.error_msg = err_msg
                return asdict(self._lambda_parameters)

            # decompress if file is compressed
            sftp_file_raw, ftp_file_data_raw = uncompress_file.uncompress_file(sftp_file, ftp_file_data)

            # Upload files from the TMP Directory to S3
            try:
                log.info(f"Uploading data to {sftp_file_raw} on S3")
                file_key = "/".join([self._s3_client.basePath, S3_FOLDER_DOWNLOAD, sftp_file_raw])
                self._s3_client.write_file_to_s3(file_key=file_key, file_content=ftp_file_data_raw)
            except Exception as ex:
                err_msg = f"Error copying files from tmp to S3.  Error {ex}"
                log.error(err_msg)
                self._lambda_parameters.error = True
                self._lambda_parameters.error_msg = err_msg
                return asdict(self._lambda_parameters)

            s3_file_list.append(file_key)

        # Write a description file to the root of the container directory
        retrieved_files_list_name = f"{S3_FOLDER_DOWNLOAD}/{BBG_DAILY_MANIFEST}"
        files_no_path_list = self.remove_path_from_file_list(files_to_retrieve_from_sftp)

        try:
            self._s3_client.write_files_to_retrieve_to_s3(files_no_path_list, retrieved_files_list_name)
        except Exception as ex:
            err_msg = f"Error writing Manifest Contents to S3 bucket.  Error {ex}"
            log.error(err_msg)
            self._lambda_parameters.error = True
            self._lambda_parameters.error_msg = err_msg
            return asdict(self._lambda_parameters)

        if len(s3_file_list) > 0:
            self._lambda_parameters.error = False
            self._lambda_parameters.files_downloaded = self._clean_file_list(file_list=s3_file_list)
            self._lambda_parameters.has_files = True
            return asdict(self._lambda_parameters)

        else:
            log.error("Error = S3 file list is empty")
            raise FileDownloadException("S3 file list is empty")

        return

    def _clean_file_list(self, file_list: List) -> List[str]:
        clean_file_list: List = []
        for file in file_list:
            log.info(f"File to clean {file}")
            bbg_type: list = file.split(".")
            if any([substring in file for substring in [".msg.", ".dscl.", ".att.", ".ib.", ".ib19."]]):
                clean_file_list.append(file)
        return clean_file_list
