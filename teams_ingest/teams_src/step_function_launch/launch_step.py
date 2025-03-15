import json
import logging
from typing import Dict

import boto3
from botocore.exceptions import ClientError, ParamValidationError
from teams_settings import *
from teams_src.step_function_launch.launch_step_funcs import (
    generate_step_function_input,
    generate_step_function_name,
)
from teams_src.teams_shared_modules.teams_data_classes import TeamsTenant

log = logging.getLogger()

"""
From an event bridge event with a constant json of
{
  "client": "ips"
  "tenant_name": "ips"
}

create a launch event in the format

{
  "client": "ips",
  "source": "teams",
  "tenant_id": "a38e65be-fb2c-4ab0-9084-199607af9f21",
  "tenant_name": "ips",
  "period": "schedule"
}


and launch the stepfunction
"""


class LaunchStepFunction:
    def __init__(self, event, boto_session: boto3.Session, stateMachineArn: str):
        self._event: Dict = event
        self._session = boto_session or boto3.Session()
        self._stateMachineArn: str = stateMachineArn or teams_settings.STEP_FN_ARN
        # Input before name as input changes the Manifest date
        if self._stateMachineArn == '':
            err_msg: str = "No Step Function ARN in EnvVar STEP_FN_ARN"
            log.exception(err_msg)
            raise ValueError(err_msg)

    def Launch_Step_Function(self) -> str:
        log.debug(f'event_payload : {self._event}')

        # Decode Event
        tenant_info: TeamsTenant = TeamsTenant(**self._event)

        # Generate Payload
        ssm_client = self._session.client("ssm")
        step_fn_event: Dict = generate_step_function_input(tenant_info=tenant_info, ssm_client=ssm_client)

        # Generate Step function Name
        step_fn_name: str = generate_step_function_name(tenant_info=tenant_info)

        step_fn_client = self._session.client('stepfunctions')

        log.info(f'step_fn_name : {step_fn_name}')
        log.info(f'step_fn_event : {step_fn_event}')
        log.info(f'stateMachineArn : {self._stateMachineArn}')
        try:
            response = step_fn_client.start_execution(
                stateMachineArn=self._stateMachineArn, name=step_fn_name, input=json.dumps(step_fn_event)
            )
        except (ClientError, ParamValidationError) as ex:
            log.exception(ex)
            raise ex

        log.info(f'response : {response}')
        return step_fn_name
