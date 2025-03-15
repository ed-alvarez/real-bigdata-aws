from voice_settings import cdrType
from voice_src.process_transcript_job.cdr_parsers.base_parser import CdrParser


class Freeswitch(CdrParser, name=cdrType.freeswitch.value):
    def __init__(self, raw_json: str, es_record=None) -> None:
        super().__init__(raw_json, es_record)
