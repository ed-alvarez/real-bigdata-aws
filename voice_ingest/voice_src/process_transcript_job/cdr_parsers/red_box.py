from datetime import datetime
from typing import Dict

from voice_settings import cdrType
from voice_src.process_transcript_job.cdr_parsers.base_parser import CdrParser
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE


class RedBox(CdrParser, name=cdrType.redbox.value):
    def __init__(self, cdr_dict: Dict, es_record=None) -> None:
        super().__init__(cdr_dict, es_record)

    def utc_to_date(self, timestamp) -> datetime:
        dt_object = datetime.fromtimestamp(int(timestamp))
        return dt_object

    def process_cdr(self) -> VOICE:
        self._voice.from_ = self._cdr["callerPhoneNumber"]
        self._voice.to = self._cdr["dialedPhoneNumber"]
        self._voice.date = self.utc_to_date(self._cdr["callStartTime"])
        return self._voice
