import logging
import sys
from pathlib import Path
from typing import Any, Dict

import boto3

# code-snippet for any local run on this mono-repo
ingest_channel_dir = Path(__file__).resolve().parent.parent
project_roo = ingest_channel_dir.parent

# add to pythonPath
sys.path.insert(0, str(project_roo))
sys.path.append(str(ingest_channel_dir))

import aws_lambda_logging
from aws_lambda_powertools.utilities.typing import LambdaContext
from src.helpers import DockerLambdaEvent, validate_event_payload

s3 = boto3.client("s3")
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """
    Download URI S3 Files using Event driven dataclass
    """
    logger.info(f"Init event {event}")

    aws_lambda_logging.setup(
        level="DEBUG",
        boto_level="INFO",
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    event: DockerLambdaEvent = validate_event_payload(event=event)
    result: DockerLambdaEvent = get_uris_from_s3(event)

    return result.to_json()


def get_uris_from_s3(event: DockerLambdaEvent) -> DockerLambdaEvent:
    """
    Get a list of S3 URIs according to the given event.
    """
    if event.fetch_ids:
        # use the boto3 s3 client to get the list of s3 uris that are inside a bucket folder
        response = s3.list_objects_v2(Bucket=event.bucket, Prefix="pdfs/")
        event.s3_uris = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"] != "pdfs/"]
    else:
        event.s3_uris = []
    return event


if __name__ == "__main__":
    event: Dict = {"bucket": "dev-docker-poc"}

    class context:
        def __init__(self):
            self.aws_request_id = "no_id"

    print(lambda_handler(event=event, context=context()))
