from dataclasses import dataclass as orig_dataclass
from dataclasses import field
from datetime import datetime
from pathlib import PurePosixPath
from typing import Dict, List

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError
from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass
from voice_settings import DYNAMO_DB_TABLE
from voice_src.helpers.helpers_client_cdr import ClientCDR

deserializer = TypeDeserializer()
serializer = TypeSerializer()


@orig_dataclass
class JobDetail:
    TranscriptionJobName: str = ""
    Media: Dict = field(default_factory=dict)
    MediaFormat: str = ""
    OutputBucketName: str = ""
    OutputKey: str = ""
    Settings: Dict = field(default_factory=dict)

    class Meta:
        ordered = True


@dataclass
class FileParts:
    full_file_name: str = ""
    directory: str = ""
    file_stem: str = ""
    file_ext: str = ""


@dataclass
class BaseRecord:
    client: str = ""
    bucket: str = ""
    audioFileKey: str = ""
    audioFileParts: FileParts = None
    audioFileURI: str = ""
    cdrFileKey: str = ""

    def generate_data(self):
        self.bucket = f"{self.client}.ips"
        self.audioFileURI = f"https://s3-eu-west-1.amazonaws.com/{self.bucket}/{self.audioFileKey}"

    def generate_cdr_file_key(self):
        file_parts: FileParts = self._generate_file_parts(key=self.audioFileKey)
        self.audioFileParts = file_parts
        cdr_file_name: str = self._generate_cdr_file_name(file_stem=file_parts.file_stem, client=self.client)
        self.cdrFileKey = f"{file_parts.directory}/{cdr_file_name}"

    def _generate_file_parts(self, key: str) -> FileParts:
        file_parts: FileParts = FileParts()
        ppp = PurePosixPath(key)
        file_parts.full_file_name = ppp.name
        file_parts.directory = ppp.parent
        file_parts.file_stem = ppp.stem
        file_parts.file_ext = ppp.suffix
        return file_parts

    def _generate_cdr_file_name(self, file_stem: str, client: str) -> str:
        client_cdr_file: ClientCDR = ClientCDR(client=client, file_stem=file_stem)
        file_name: str = client_cdr_file.FileName
        return file_name


@dataclass
class DynamoTranscriptionRecord(BaseRecord):
    transcriptionJob: str = ""
    transcriptionStartTime: datetime = None
    transcriptionFileKey: str = ""

    def __getitem__(self, item):
        return getattr(self, item)

    def generate_transcription_file_key(self):
        file_parts: FileParts = self._generate_file_parts(key=self.audioFileKey)
        self.transcriptionFileKey = f"{file_parts.directory}/{self.transcriptionJob}.json"

    def get_dynamo_transcription_job(self):
        try:
            ddb = boto3.client("dynamodb")
            get_result = ddb.get_item(TableName=DYNAMO_DB_TABLE, Key={"transcriptionJob": {"S": self.transcriptionJob}})
        except ClientError as err:
            raise err
        else:
            deserialised = {k: deserializer.deserialize(v) for k, v in get_result.get("Item").items()}
            object = self.Schema().load(deserialised, unknown=EXCLUDE)
            return object

    def put_dynamo_transcription_job(self):
        try:
            ddb = boto3.client("dynamodb")
            response = ddb.put_item(
                TableName=DYNAMO_DB_TABLE, Item={k: serializer.serialize(v) for k, v in self.Schema().dump(self).items() if v != ""}
            )
        except ClientError as err:
            raise err
        else:
            return response
