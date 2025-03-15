import logging
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import dataclass_wizard

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from zoom_settings import (
    ES_CLOUD_ID,
    ES_OP_TYPE,
    ES_PASSWORD,
    ES_USER,
    INGEST_SOURCE,
    INPUT_INDEX,
    STAGE,
    zoomType,
)
from zoom_shared.zoom_dataclasses import CDR, Transcript, ZoomDTO
from zoom_shared.zoom_es_models import (
    ZOOM,
    BodyDetail,
    FingerprintMeta,
    PersonaID,
    Phrase,
    Schema,
)
from zoom_shared.zoom_utils import error_handler

from shared.shared_src.es.es_client import ElasticSearchClient
from shared.shared_src.es.es_dsl_client import ESUploadDSl

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@error_handler
def parser_blob_to_es_docs(firm: str, data: ZoomDTO, aws_request_id: str) -> ZOOM:
    """
    Zoom ES Docs obj builder
    """
    zoom: ZOOM = None
    transcript: Transcript = data.transcript
    participant_personas = []

    phrases_list, full_transcript = transcript_extract_body_phrases(transcript)
    fingerprint_signature: FingerprintMeta = _build_fingerprint_meta(firm, data, aws_request_id)
    persona_to: PersonaID = _build_person_id(data, "destination_to")
    persona_from: PersonaID = _build_person_id(data, "origin_from")
    if "meet" in fingerprint_signature.type:
        participant_personas: List[PersonaID] = _build_personas_participants(data)
    phrases: Phrase = _build_phrases(phrases_list)
    body_detail: BodyDetail = _build_body_detail(phrases)
    zoom = build_zoom_doc(
        cdr=data.cdr,
        persona_to=persona_to,
        persona_to_detail=participant_personas,
        persona_from=persona_from,
        body=full_transcript,
        body_detail=body_detail,
        fingerprint_signature=fingerprint_signature,
    )
    return zoom


def _build_fingerprint_meta(firm: str, data: ZoomDTO, aws_request_id: str) -> FingerprintMeta:
    cdr: CDR = data.cdr
    transcript: Transcript = data.transcript
    now_ts: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return FingerprintMeta(
        bucket=f"dev-{firm}.ips" if "dev" in STAGE else f"{firm}.ips",
        client=firm,
        key=data.recording.source.source_id,
        key_audio=data.recording.source.source_id,
        key_cdr=data.cdr.source.source_id,
        key_transcript=data.transcript.source.source_id,
        processed_time=now_ts,
        time=transcript.start_time,
        type=f"{INGEST_SOURCE}.{cdr.source.source_type}",
        type_transcription=transcript.type,
        aws_lambda_id=aws_request_id,
        schema=Schema.version,
    )


def _build_personas_participants(data: Dict) -> List[PersonaID]:
    participants: List[PersonaID] = []
    cdr: dict = asdict(data.cdr)
    for persona in cdr["participants"]:
        persona = PersonaID(
            email_address=persona.get("user_email", ""),
            alternative_id=persona.get("id", ""),
            firstname=persona.get("name", ""),
            lastname="",
            domain="NA",
            tel_number="NA",
        )
        participants.append(persona)
    return participants


def _build_person_id(data: Dict, target: str) -> PersonaID:
    cdr: dict = asdict(data.cdr)
    return PersonaID(
        email_address=cdr.get(target, {}).get("persona_email"),
        alternative_id=cdr.get(target, {}).get("persona_id"),
        firstname=cdr.get(target, {}).get("persona_first_name"),
        lastname=cdr.get(target, {}).get("persona_second_name"),
        domain=cdr.get(target, {}).get("persona_department"),
        tel_number=cdr.get(target, {}).get("persona_number"),
    )


def _build_phrases(content: Union[Dict, str]) -> List[Phrase]:
    phrases: Phrase = []
    for phrase in content:
        text: str = phrase.get("text").replace("'", "")
        user: str = phrase.get("users")[0].get("username") if phrase.get("users") else phrase.get("speaker")
        start_ts: str = phrase.get("ts", "")  # to check what format
        end_ts: str = phrase.get("end_ts", "")

        hour = start_ts.split(":")[0]
        minutes = start_ts.split(":")[1]
        seconds = start_ts.split(":")[2]
        start_ts_seconds = round(float(int(hour) * 3600 + int(minutes) * 60 + float(seconds)), 2)

        hour = end_ts.split(":")[0]
        minutes = end_ts.split(":")[1]
        seconds = end_ts.split(":")[2]
        end_ts_seconds = round(float(int(hour) * 3600 + int(minutes) * 60 + float(seconds)))

        phrase = Phrase(
            start_time=start_ts_seconds,
            end_time=end_ts_seconds,
            text=text,
            speaker=user,
        )
        phrases.append(phrase)
    return phrases


def _build_body_detail(phrases: list) -> BodyDetail:
    return BodyDetail(
        phrases=phrases,
        has_body=bool(phrases),
    )


def build_zoom_doc(
    cdr: CDR,
    persona_to: PersonaID,
    persona_to_detail: Optional[List[PersonaID]],
    persona_from: PersonaID,
    body: str,
    body_detail: BodyDetail,
    fingerprint_signature: FingerprintMeta,
) -> ZOOM:
    _to_full_name: str = f"{cdr.destination_to.persona_first_name} " + cdr.destination_to.persona_second_name.replace(
        "Unknown",
        "",
    )

    _from_full_name: str = f"{cdr.origin_from.persona_first_name} " + cdr.origin_from.persona_second_name.replace(
        "Unknown",
        "",
    )

    _to: str = f"{_to_full_name}"
    _from: str = f"{_from_full_name}"

    date_of_event: str = cdr.date_of_action
    return ZOOM(
        to=_to,
        to_detail=persona_to if persona_to_detail is not [] else persona_to_detail,
        from_=_from,
        from_detail=persona_from,
        body=body,
        body_detail=body_detail,
        date=date_of_event,
        fingerprint=fingerprint_signature,
    )


def transcript_extract_body_phrases(transcript: Transcript):
    content: list = []
    full_transcript: str = []

    if transcript.source.source_type == zoomType.meet.value:
        content = transcript.content["content"]
    else:
        content = transcript.content

    full_transcript: str = "".join([" " + content["text"] for content in content])
    return content, full_transcript.replace("'", "")


def push_to_elastic_search(firm: str, final_blob: ZoomDTO, obj_id: str, aws_request_id: str):
    logger.info(f"Parsing from final blob to ES Document {obj_id}---")
    logger.debug(f"Final blob being parsed\n {final_blob} --- \n")

    zoom_doc: ZOOM = parser_blob_to_es_docs(firm, final_blob, aws_request_id)
    elasticsearch_client = ElasticSearchClient(ES_PASSWORD, ES_USER, ES_CLOUD_ID)
    dsl = ESUploadDSl(elasticsearch_client)
    dsl.insert_document(document=zoom_doc, index_table=INPUT_INDEX, es_type=ES_OP_TYPE, obj_id=obj_id)


if __name__ == "__main__":

    elasticsearch_client = ElasticSearchClient(ES_PASSWORD, 'elastic', ES_CLOUD_ID)
    dsl = ESUploadDSl(elasticsearch_client)
