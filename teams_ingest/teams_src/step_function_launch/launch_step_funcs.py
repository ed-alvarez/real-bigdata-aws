from dataclasses import asdict
from datetime import datetime
from typing import Dict

import boto3
from teams_src.teams_shared_modules.teams_data_classes import TeamsEvent, TeamsTenant


def generate_step_function_name(tenant_info: TeamsTenant) -> str:
    raw_date_part: str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    step_fn_name: str = f"{tenant_info.client}_{tenant_info.tenant_name}_{raw_date_part}"
    return step_fn_name


def get_tenant_id_from_ssm(tenant_info: TeamsTenant, ssm_client: boto3.client) -> str:
    ssm = ssm_client or boto3.client('ssm')
    parameter_name: str = f'/teams/{tenant_info.client}/{tenant_info.tenant_name}/TENANT_ID'
    tenant_id: str = ssm.get_parameter(Name=parameter_name, WithDecryption=True)['Parameter']['Value']
    return tenant_id


def generate_step_function_input(tenant_info: TeamsTenant, ssm_client: boto3.client) -> Dict:
    tenant_id: str = get_tenant_id_from_ssm(tenant_info=tenant_info, ssm_client=ssm_client)
    raw_lambda_event: TeamsEvent = TeamsEvent(
        client=tenant_info.client, tenant_name=tenant_info.tenant_name, tenant_id=tenant_id
    )
    lambda_event: Dict = asdict(raw_lambda_event)
    return lambda_event
