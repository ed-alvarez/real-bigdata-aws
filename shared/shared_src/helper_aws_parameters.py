import logging

import boto3
from boto3 import client
from botocore.exceptions import ClientError

log = logging.getLogger()


class AWS_Key_Parameters:
    def __init__(self, client_name: str = None, ssm_helper=None):
        self._ssm_helper = ssm_helper or boto3.client("ssm")
        self._client_name: str = client_name

    @staticmethod
    def param_key_gen(item_key: str, ssm_branch: str = None) -> str:
        param_key = "/".join([ssm_branch, item_key])
        return f"/{param_key}"

    def _get_individual_parameter(self, item_key: str, client_name: str, decryption: bool = False) -> str:
        parameter_value: str = ""
        if not client_name:
            return ""
        log.debug(f"item_key is {item_key}, ssm_branch is {client_name}")
        parameter_key: str = self.param_key_gen(item_key=item_key, ssm_branch=client_name)
        log.debug(f"param_key is {parameter_key}")
        try:
            parameter_details = self._ssm_helper.get_parameter(Name=parameter_key, WithDecryption=decryption)
        except ClientError as ex:
            log.warning(ex)
            log.debug(f"No Parameter found for {parameter_key}")
            return parameter_value

        param_value: str = parameter_details["Parameter"]["Value"]
        log.debug(f"Parameter key {parameter_key} value is {param_value}")
        return param_value

    def get_ssm_parameter(self, parameter_path):
        try:
            self._ssm_helper.get_parameter(Name=parameter_path)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                return None
            else:
                raise

    def put_parameter(
        self,
        name: str,
        description: str,
        value: str,
        type: str = "String",
        overwrite: bool = True,
    ) -> None:
        """Put parameter for client and if not place the default entry"""
        parameter_key: str = self.param_key_gen(item_key=name, ssm_branch=self._client_name)
        log.debug(f"Putting {name} at {parameter_key}")
        try:
            parameter_details = self._ssm_helper.put_parameter(
                Name=parameter_key,
                Description=description,
                Value=value,
                Type=type,
                Overwrite=overwrite,
            )
            log.debug(parameter_details)
        except ClientError as ex:
            log.error(f"Error Upserting Parameter {ex}")

    def get_parameter_value(self, item_key: str, client_name: str = None, decryption: bool = False) -> str:
        """Get parameter for client and if not try the default entry"""
        client_name: str = client_name or self._client_name
        store_fetch: str = self._get_individual_parameter(item_key=item_key, client_name=client_name)
        if store_fetch:
            log.debug(f"Found parameter {item_key} for {client_name}")

        if not store_fetch:
            # try and get the parameter from Default
            log.info(f"Cannot find parameter for {client_name}, trying default parameter")

            client_name = "default"
            self._client_name = client_name
            store_fetch = self._get_individual_parameter(item_key=item_key, client_name=client_name, decryption=decryption)

            if store_fetch:
                log.debug(f"Found parameter {item_key} for {client_name} value {store_fetch}")

            if not store_fetch:
                error_msg: str = f"No {client_name}/{item_key} found for user default"
                log.warning(error_msg)
                store_fetch = ""

        return store_fetch


# To Put params at store! add client/param/path
# ssm_client = AWS_Key_Parameters(client_name='')
# ssm_client.put_parameter(name="", description="",
# value="", type='String')
