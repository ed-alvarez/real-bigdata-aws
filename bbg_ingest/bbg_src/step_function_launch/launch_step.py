import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta

import bbg_settings
import boto3

log = logging.getLogger()
from bbg_helpers.helper_dataclass import StepFunctionParameters


class LaunchStepFunction:
    def __init__(self, event):
        self._event = event
        self._event_payload = ""
        self._time = datetime.now()
        self._lambda_parameters = None
        self._client = boto3.client("stepfunctions")

    def decode_event(self, event):
        """If there is a body key then the submission is from the API rather than EventBridge"""
        event_payload = ""
        if "body" in event:
            event_payload = json.loads(event["body"])
        else:
            event_payload = event
        return event_payload

    def generate_step_function_name(self, lambda_parameters):
        now = "{:%Y_%m_%d_%H_%M_%S}".format(self._time)
        if lambda_parameters.manifest_date:
            manifest = "_".join([lambda_parameters.bbg_manifest, lambda_parameters.manifest_date])
        else:
            manifest = lambda_parameters.bbg_manifest
        name = "_".join([lambda_parameters.client_name, manifest.lower(), now])
        return name

    def generate_manifest_date(self):
        """Due to BBG unreliability on file generation take data from 2 days ago"""
        days = timedelta(2)
        manifest_date = self._time - days
        bbg_manifest_date = "{:%y%m%d}".format(manifest_date)
        return bbg_manifest_date

    def generate_step_function_input(self):
        if self._lambda_parameters.manifest_date == "":
            self._lambda_parameters.manifest_date = self.generate_manifest_date()
        try:
            json_input = json.dumps(asdict(self._lambda_parameters))
        except Exception as ex:
            log.exception(ex)
            raise ex

        return json_input

    def Launch_Step_Function(self):
        # Decode Event
        self._event_payload = self.decode_event(self._event)
        log.debug(f"event_payload : {self._event_payload}")
        self._lambda_parameters = StepFunctionParameters(**self._event_payload)
        log.debug(f"parameters : {self._lambda_parameters}")

        stateMachineArn = bbg_settings.STEP_FN_ARN
        log.info(f"stateMachineArn : {stateMachineArn}")
        # Input before name as input changes the Manifest date
        input = self.generate_step_function_input()
        log.info(f"input : {input}")
        name = self.generate_step_function_name(self._lambda_parameters)
        log.info(f"name : {name}")

        try:
            response = self._client.start_execution(stateMachineArn=stateMachineArn, name=name, input=input)
        except Exception as ex:
            log.exception(ex)
            raise ex

        log.info(f"response : {response}")
        return name


if __name__ == "__main__":

    def test_1():
        # event = '{"bbg_manifest": "DAILY", "bbg_client_id": "mc760833277", "client_name": "hashemicap"}'
        # event = {"bbg_manifest": "DAILY", "bbg_client_id": "mc913915589","client_name": "valeur"}
        event = {
            "bbg_manifest": "DAILY",
            "bbg_client_id": "mc913915589",
            "client_name": "valeur",
            "manifest_date": "200907",
        }
        # event = {"detail": {"bbg_manifest": "ARCHIVE", "bbg_client_id": "mc913915589","client_name": "valeur","manifest_date": "200826"},
        #         "time" : "1970-01-01T00:00:00Z"}
        launch = LaunchStepFunction(event)
        output = launch.Launch_Step_Function()
        # name = launch.generate_step_function_name()
        # input = launch.generate_step_function_input()
        # response = launch.Launch_Step_Function()
        print(name)
        print(input)
        print(response)

    def test_2():
        with open("/bbg_tests/fixtures/api/POST.json") as lambda_event:
            event = json.loads(lambda_event.read())
            launch = LaunchStepFunction(event)
            output = launch.Launch_Step_Function()

    test_2()
