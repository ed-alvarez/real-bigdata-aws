"""
s3 objects processing class
"""
import datetime
import logging
import sys
import time

import boto3
from botocore.exceptions import ClientError, ParamValidationError

from whatsapp_ingest.whatsapp_helpers.helper_objects import newEventDetail
from whatsapp_ingest.whatsapp_helpers.ips_tools import print_class

log = logging.getLogger()


class S3Object:
    SYSTEM_S3_ROOT = "ips"  # shouldn't be hard coded here

    def __init__(self, event_object: newEventDetail):
        self._aws_lambda_event: newEventDetail = event_object
        self._email_body = None
        self._mime_file_date = None
        self._file_object = None
        self._file_content = None

        try:
            log.debug("Initialising S3Object Instance...")
            self.s3 = boto3.client("s3")

        except Exception as ex:
            log.exception("S3Object class initialisation failed!")
            raise ex

    @property
    def emailBody(self):
        return self._email_body

    @property
    def mimeFileDate(self):
        return self._mime_file_date

    @property
    def fileObj(self):
        return self._file_object

    @property
    def fileContent(self):
        return self._file_content

    def __str__(self):
        return print_class(self)

    def list_files_with_prefix(self, prefix):
        s3_prefix = prefix
        """List files in specific S3 URL"""
        s3_objects = []
        try:
            response = self.s3.list_objects_v2(Bucket=self._aws_lambda_event.bucket, Prefix=s3_prefix)
            for content in response.get("Contents", []):
                if content["Size"] > 0:
                    s3_objects.append(content.get("Key"))

        except ParamValidationError as ex:
            log.debug("FAIL get directory contents")
            log.error(
                "Param Validation Error listing objects in bucket %s. Reason : %s",
                self._aws_lambda_event.bucket,
                ex,
            )
            log.debug("Exit list_files_with_prefix with Error")
            raise ex

        except ClientError as ex:
            log.debug("FAIL get directory contents")
            log.error("Client Error listing objects in bucket %s. Reason : %s", self._aws_lambda_event.bucket, ex)
            log.debug("Exit list_files_with_prefix with Error")
            raise ex

        except Exception as e:
            log.error("Error = " + str(e))
            log.debug("Exit list_files_with_prefix with Error")
            raise e

        return s3_objects

    def collect_object(self, file_key: str):
        """
        Retrieve the s3 object and set up class properties.
        """
        try:
            response = self.get_file_data(file_name=file_key)
        except Exception as ex:
            log.error(ex)
            raise

        self._mime_file_date = response.get("LastModified")
        log.debug("Content Type : " + response.get("ContentType", ""))
        log.debug("Response : " + str(response))
        self._email_body = self._file_content.decode("utf-8")
        log.debug("Email body read")

    def copy_file_between_folders(self, src_key, dst_key):
        log.debug("copy_file_between_folders, src_key, {}, dst_key, {}".format(src_key, dst_key))
        bucket = self._aws_lambda_event.client + "." + S3Object.SYSTEM_S3_ROOT  # rule shouldn't be hard coded here
        source_obj = {
            "Bucket": bucket,
            "Key": src_key,
        }
        try:
            response = self.s3.copy_object(CopySource=source_obj, Bucket=bucket, Key=dst_key)
        except Exception as ex:
            error_type, error_instance, traceback = sys.exc_info()
            log.error(ex)
            raise error_type(error_instance.info).with_traceback(traceback)
        return response

    def delete_file(self, key):
        log.debug("delete_file, key, {}".format(key))
        bucket = self._aws_lambda_event.client + "." + S3Object.SYSTEM_S3_ROOT  # rule shouldn't be hard coded here
        try:
            response = self.s3.delete_object(Bucket=bucket, Key=key)
        except Exception as ex:
            error_type, error_instance, traceback = sys.exc_info()
            log.error(ex)
            raise error_type(error_instance.info).with_traceback(traceback)
        return response

    def copy_to_bucket(
        self,
        file_key,
        stream="email",
        file_only=False,
        status="complete",
        email_date=datetime.datetime.now(),
        new_bucket=None,
        delete_after_copy=False,
    ):
        """
        Copy the object over to a stash folder for temporary archiving
        stream is email, bbg or voice
        """

        if file_only:
            file_name = file_key.split("/")[1]
        else:
            file_name = file_key

        try:
            date_folder = f"{email_date:%Y-%m-%d}"
            source = {"Bucket": self._aws_lambda_event.bucket, "Key": file_key}
            dest_bucket_name = new_bucket + "." + self._aws_lambda_event.client + "." + S3Object.SYSTEM_S3_ROOT

            if status != "complete":
                dest_key = stream + "/" + date_folder + "/" + status + "/" + file_name
            else:
                dest_key = stream + "/" + date_folder + "/" + file_name
            worked = False
            timeout = 0
            response = None
            while not worked:
                try:
                    log.info(f"Attempting to copy Source: {source} to bucket: {dest_bucket_name}, dest_key: {dest_key}")
                    response = self.s3.copy_object(CopySource=source, Bucket=dest_bucket_name, Key=dest_key)
                    worked = True
                except Exception as ex:
                    timeout = timeout + 1
                    time.sleep(1)
                    log.info(f"Create_temp_object having to wait.  Seconds passed = {timeout}")

                    if timeout > 5:
                        worked = True
                        log.exception(f"Could not create the archive copy after {timeout} seconds")
                        raise ex
                    else:
                        log.info(f"Attempting again...")

            if response["CopyObjectResult"]["ETag"] is not None:
                log.info(f"{self._aws_lambda_event.bucket}/{file_key} copied to {dest_bucket_name}/{dest_key}")
            else:
                log.warning(f"{self._aws_lambda_event.bucket}/{file_key} failed to copy to safekeeping  correctly!")

        except Exception as ex:
            log.exception(
                f"Could not create a temp archive for the message object. Source:{source}. "
                f"Dest bucket: {dest_bucket_name} dest key {dest_key}  Aborting!"
            )
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)

        if delete_after_copy:
            try:
                response = self.s3.delete_object(Bucket=self._aws_lambda_event.bucket, Key=file_key)
                log.info("Delete Original file %s, Status: %s", file_key, response)

            except ParamValidationError as ex:
                log.exception("Error trying to DELETE $s. Reason: %s", file_key, ex)
                error_type, error_instance, traceback = sys.exc_info()
                raise error_type(error_instance.info).with_traceback(traceback)

            except ClientError as ex:
                log.exception("Error trying to DELETE $s. Reason: %s", file_key, ex)
                error_type, error_instance, traceback = sys.exc_info()
                raise error_type(error_instance.info).with_traceback(traceback)

    def get_file_data(self, file_name):
        log.debug("Enter get_file")

        try:
            log.debug("get object %s", file_name)
            self._file_object = self.s3.get_object(Bucket=self._aws_lambda_event.bucket, Key=file_name)
            self._file_content = self._file_object["Body"].read()
            log.debug("SUCCESS get object %s", file_name)

        except ParamValidationError as ex:
            log.debug("FAIL get object %s", file_name)
            log.error(
                "Param Validation Error listing objects in bucket %s. Reason : %s",
                self._aws_lambda_event.bucket,
                ex,
            )
            log.debug("Exit get_file with Error")
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)

        except ClientError as ex:
            log.debug("FAIL get object %s", file_name)
            log.error("Client Error listing objects in bucket %s. Reason : %s", self._aws_lambda_event.bucket, ex)
            log.debug("Exit get_file with Error")
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)

        log.debug("Exit get_file")
        return self._file_object

    @staticmethod
    def xstr(s):
        return lambda s: str(s) or ""
