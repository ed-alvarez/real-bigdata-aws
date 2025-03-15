import json
from pathlib import Path
from typing import Dict

from voice_src.process_transcript_job.cdr_parsers.ring_central import RingCentral
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE

BASE_DIR = Path(__file__).resolve().parent.parent.parent

with open(f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/2020-06-25.meta.f0f5cba1-a457-4f44-edb8-12def04cd9e0.json") as cdr:
    cdr_dict: Dict = json.load(cdr)


class TestFunctions:
    def test_ring_central(self, ssm_voice_setup):
        with ssm_voice_setup:
            call_obj: RingCentral = RingCentral(cdr_dict=cdr_dict)
            response: VOICE = call_obj.process_cdr()
            assert response.from_ == "10104"
