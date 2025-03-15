import json
import logging
from datetime import datetime
from typing import Dict

import dataclass_wizard
from boto3 import Session
from botocore.exceptions import ClientError, ParamValidationError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""
From an event bridge event with a constant json of
    {
        "customer": "ips",
        "tenant": "zoom",
        "period": "daily"
    }

create a launch event in the format

    {
        "customer": "ips",
        "tenant": "zoom",
        "period": "daily"
        "tenant_ssm_secret_A": "123",
        "tenant_ssm_secret_B": "345"
        ...
        "tenant_ssm_secret_N": "567"
    }

and launch the stepfunction
"""


class LaunchStepFunction:
    def __init__(self, event, state_machine_arn: str, boto_session: Session = None):
        self._event: Dict = event
        self._session: Session = boto_session or Session()
        self._state_machine_arn: str = state_machine_arn

        if not self._state_machine_arn:
            err_msg: str = "No Step Function ARN in EnvVar STEP_FN_ARN"
            logger.exception(err_msg)
            raise ValueError(err_msg)

    def start_execution_step_function(self, launch_tenant_dt) -> tuple:
        logger.debug(f"event_payload : {self._event}")

        # Decode Trigger Event
        launch_event = dataclass_wizard.fromdict(launch_tenant_dt, self._event)

        # Generate Step function Name
        step_fn_name: str = self._generate_step_function_name(launch_event=launch_event)
        logger.info(f"step_fn_name : {step_fn_name} | state_machine_arn : {self._state_machine_arn}")

        step_fn_client = self._session.client("stepfunctions")
        logger.debug(f"Starting the Step function with: {launch_event}")

        try:
            response = step_fn_client.start_execution(
                stateMachineArn=self._state_machine_arn, name=step_fn_name, input=json.dumps(launch_event.to_json())
            )

        except (ClientError, ParamValidationError) as error:
            logger.error(f"Execution details : {error}")
            raise error

        logger.info(f"Execution details : {response}")

        return step_fn_name, response['executionArn']

    def _generate_step_function_name(self, launch_event) -> str:
        firm: str = launch_event.firm
        tenant: str = launch_event.tenant_name  # if sub-account, else ingest-channel
        start_date: str = launch_event.start_date
        end_date: str = launch_event.end_date
        raw_date_part: str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        logger.info(f"Generating name for state machine {tenant}")
        step_fn_name: str = f"{firm}_{tenant}_{start_date}_{end_date}__tsmp_{raw_date_part}"
        return step_fn_name
