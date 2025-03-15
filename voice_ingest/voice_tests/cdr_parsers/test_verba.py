import json
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, Union

from lxml import etree as ET
from voice_src.process_transcript_job.cdr_parsers.verba import Verba
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def etree_to_dict(root, include_root_tag=False):
    root = root
    result = OrderedDict()
    if len(root) > 1 and len({child.tag for child in root}) == 1:
        result[next(iter(root)).tag] = [etree_to_dict(child) for child in root]
    else:
        for child in root:
            result[child.tag] = etree_to_dict(child) if len(list(child)) > 0 else (child.text or "")
    result.update(("@" + k, v) for k, v in root.attrib.items())
    return {root.tag: result} if include_root_tag else result


xml_data = ET.parse(f"{BASE_DIR}/voice_tests/test_data/verba/8912351--009711056757#_2022-01-13_14-02.xml")
cdr_dict: Dict = etree_to_dict(xml_data.getroot())
print(cdr_dict)


class TestFunctions:
    def test_verba(self, ssm_voice_setup):
        with ssm_voice_setup:
            call_obj: Verba = Verba(cdr_dict=cdr_dict)
            response: VOICE = call_obj.process_cdr()
            assert response.from_ == "8912351"
