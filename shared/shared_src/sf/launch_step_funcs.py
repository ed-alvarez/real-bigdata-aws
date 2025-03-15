import logging
from datetime import datetime
from typing import Any, Dict

import dataclass_wizard

from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

########
# Utils


def generate_step_function_name(step_fn_event: Dict) -> str:
    customer: str = step_fn_event["customer"]
    tenant: str = step_fn_event["tenant"]
    raw_date_part: str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    logger.info(f"Generating name for state machine {tenant}")
    step_fn_name: str = f"{customer}_{tenant}_{raw_date_part}"
    return step_fn_name


def generate_step_function_input(TenantDataclass: Any, launch_medatada: Any) -> Dict:
    customer: str = launch_medatada.customer
    tenant: str = launch_medatada.tenant
    logger.info(f"Pulling SSM secrets for {customer} state machine {tenant}")

    for key in launch_medatada.to_json():
        if "ssm" in key:  # gets the SSM creds needed
            secret: str = key.split("ssm_")[1]
            launch_medatada.key = AWS_Key_Parameters(client_name=customer).get_parameter_value(item_key=f"{tenant}/{secret}")
            logger.info(f"Pulled {key} secrets with {launch_medatada.key} value")
    raw_lambda_event: Any = dataclass_wizard.fromdict(TenantDataclass, launch_medatada.to_json())
    return launch_medatada.to_json(), raw_lambda_event.to_json()
