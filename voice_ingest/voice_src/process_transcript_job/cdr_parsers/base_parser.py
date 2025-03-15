from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Dict, Type

from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE


class CdrParser:
    _registry: ClassVar[Dict[str, Type[CdrParser]]] = {}

    def __init_subclass__(cls, name: str, **kwargs) -> None:
        cls.name: str = name  # type: ignore
        CdrParser._registry[name] = cls
        super().__init_subclass__(**kwargs)  # type: ignore

    def __init__(self, cdr_dict=None, es_record=None) -> None:
        super().__init__()
        self._cdr: Dict = cdr_dict
        self._voice: VOICE = es_record or VOICE()

    @classmethod
    def get(cls, name: str):
        return CdrParser._registry[name]

    @property
    def esVoice(self) -> VOICE:
        return self._voice

    def utc_to_date(self, timestamp) -> datetime:
        raise NotImplementedError()

    def process_cdr(self) -> VOICE:
        raise NotImplementedError()
