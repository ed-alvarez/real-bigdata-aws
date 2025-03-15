import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from tika import parser

s3 = boto3.client("s3")
TIKA_SERVER_JAR = os.getenv("TIKA_SERVER_JAR")
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """
    Parse S3 PDF Files using tika from Event driven architecture
    """
    logger.info(f"Input event {event}")

    aws_lambda_logging.setup(
        level="DEBUG",
        boto_level="INFO",
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    event: DockerLambdaEvent = validate_event_payload(event=event)
    if texts := parse_text_from_pdf(event):
        event.texts.append(texts)
    return event.to_json()


def parse_text_from_pdf(event: DockerLambdaEvent) -> Optional[List[str]]:
    """
    Extract text from one-s3-uri PDF file at the time using Tika parser.
    """
    if event.s3_uris:
        try:
            response = s3.get_object(Bucket=event.bucket, Key=event.s3_uris.pop())
            content = response["Body"].read()
            parsed = parser.from_buffer(content)  # this requires a running Tika server to extract text
            return parsed["content"]
        except Exception as e:
            logger.exception(f"Error processing {event.s3_uris}. {e}")
    else:
        event.done_workflow = True
        return None


if __name__ == "__main__":
    event: Dict = {
        "bucket": "dev-docker-poc",
        "fetch_ids": True,
        "s3_uris": [
            "pdfs/tika_test.pdf",
            "pdfs/tika_test_copy_2.pdf",
            "pdfs/tika_test_copy_3.pdf",
            "pdfs/tika_test_copy_4.pdf",
            "pdfs/tika_test_copy_5.pdf",
            "pdfs/tika_test_copy_6.pdf",
        ],
        "texts": [],
        "done_workflow": False,
    }

    class context:
        def __init__(self):
            self.aws_request_id = "no_id"

    print(lambda_handler(event=event, context=context()))
