import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict
from urllib.parse import unquote_plus

from whatsapp_ingest import whatsapp_settings

log = logging.getLogger()
if os.environ.get("AWS_EXECUTION_ENV") is None:
    ch = logging.StreamHandler()
    log.addHandler(ch)


@dataclass
class newEventDetail:
    event: Dict
    bucket: str = field(init=False)
    client: str = field(init=False)
    message_id: str = field(init=False)

    def __post_init__(self):
        if self.event:
            self.bucket = self.event["Records"][0]["s3"]["bucket"]["name"]
            self.client = self.bucket.split(".")[0]
            self.message_id = unquote_plus(self.event["Records"][0]["s3"]["object"]["key"]).split("/")[-1]
        else:
            self.bucket = ""
            self.client = ""
            self.message_id = ""


@dataclass
class newPathDetail:
    message_id: str
    _date: datetime = datetime.now()
    _root_folder: str = whatsapp_settings.S3_BUCKET_TODO

    def _is_dev_mode(self):
        return os.environ.get("STAGE") == "dev" or os.environ.get("AWS_EXECUTION_ENV") is None

    def set_date(self, date_time: datetime):
        self._date = date_time

    def set_root_folder(self, root_folder: str):
        self._root_folder = root_folder

    @property
    def base_path(self) -> str:
        prepend: str = "dev." if self._is_dev_mode else ""
        return f"{prepend}{self._root_folder}/"

    @property
    def dated_base_path(self) -> str:
        str_date: str = datetime.strftime(self._date, "%Y-%m-%d")
        return f"{self.base_path}{str_date}/"

    @property
    def key(self):
        return f"{self.base_path}{self.message_id}"

    @property
    def dated_key(self) -> str:
        return f"{self.dated_base_path}{self.message_id}"
