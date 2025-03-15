import json
from pathlib import Path
from typing import Dict

from voice_src.process_transcript_job.cdr_parsers.base_parser import CdrParser
from voice_src.process_transcript_job.cdr_parsers.red_box import RedBox
from voice_src.process_transcript_job.cdr_parsers.ring_central import RingCentral

BASE_DIR = Path(__file__).resolve().parent.parent.parent

with open(
    f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/speaker_ident/ips-2021-03-09.13837a13-9049-70c6-8123-545eebc42abd-1615834524-443608.json"
) as cdr:
    cdr_dict: Dict = json.load(cdr)


class TestFunctions:
    def test_factory_redbox(self, ssm_voice_setup):
        with ssm_voice_setup:
            from voice_settings import cdrType

            parser: CdrParser = CdrParser.get(cdrType.redbox.value)(cdr_dict=cdr_dict)
            assert isinstance(parser, RedBox)

    def test_factory_ringcentral(self, ssm_voice_setup):
        with ssm_voice_setup:
            from voice_settings import cdrType

            parser: CdrParser = CdrParser.get(cdrType.ringcentral.value)(cdr_dict=cdr_dict)
            assert isinstance(parser, RingCentral)
