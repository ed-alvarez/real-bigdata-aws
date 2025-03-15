import datetime
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict

import boto3
from freezegun import freeze_time

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.step_function_launch.launch_step import LaunchStepFunction
from teams_src.step_function_launch.launch_step_funcs import (
    generate_step_function_input,
    generate_step_function_name,
    get_tenant_id_from_ssm,
)
from teams_src.teams_shared_modules.teams_data_classes import TeamsTenant

FAKE_TIME = datetime.datetime.now() - datetime.timedelta(minutes=57)
SF_NAME_TS = FAKE_TIME.strftime("%Y_%m_%d_%H_%M_%S")
TENANT_INFO: TeamsTenant = TeamsTenant(client="test_client", tenant_name="test_tenant")


class TestFunctions:
    def test_generate_step_function_name(self):
        with freeze_time(FAKE_TIME):
            response: str = generate_step_function_name(tenant_info=TENANT_INFO)
        assert response == f"test_client_test_tenant_{SF_NAME_TS}"

    def test_generate_step_function_input(self, ssm_teams_setup, teams_ssm_client):
        with ssm_teams_setup:
            response: Dict = generate_step_function_input(
                tenant_info=TENANT_INFO, ssm_client=teams_ssm_client
            )
        assert response['period'] == "schedule"
        assert response['tenant_id'] == 'long_guid'

    def test_get_tenant_id_from_ssm(self, ssm_teams_setup, teams_ssm_client):
        with ssm_teams_setup:
            response: str = get_tenant_id_from_ssm(tenant_info=TENANT_INFO, ssm_client=teams_ssm_client)
        assert response == 'long_guid'


class TestLambdaFunction:
    def test_lambda_function(self, ssm_teams_setup, step_fn_client, state_machine_creator):
        event: Dict = asdict(TENANT_INFO)
        with freeze_time(FAKE_TIME):
            with ssm_teams_setup:
                raw_launch_fn: LaunchStepFunction = LaunchStepFunction(
                    event=event, boto_session=boto3.Session(), stateMachineArn=state_machine_creator
                )
            response: str = raw_launch_fn.Launch_Step_Function()
        assert response == f"test_client_test_tenant_{SF_NAME_TS}"
