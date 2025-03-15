from datetime import datetime
from typing import Dict, List

from datefinder import find_dates
from voice_settings import cdrType
from voice_src.process_transcript_job.cdr_parsers.base_parser import CdrParser
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE


class RingCentral(CdrParser, name=cdrType.ringcentral.value):
    def __init__(self, cdr_dict: Dict, es_record=None) -> None:
        super().__init__(cdr_dict, es_record)

    def utc_to_date(self, timestamp) -> datetime:
        matches: List[datetime] = list(find_dates(timestamp))
        if matches:
            return matches[0]
        else:
            return datetime.now()

    def process_cdr(self) -> VOICE:
        self._voice.from_ = self._cdr["Participants"]["caller"][0]["Extension"]
        self._voice.to = self._cdr["Participants"]["callee"][0]["Extension"]
        self._voice.date = self.utc_to_date(self._cdr["CreateDate"])
        return self._voice
