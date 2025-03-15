import sys
from pathlib import Path

from elasticsearch_dsl import Float  # epoch timestamp
from elasticsearch_dsl import (
    Boolean,
    CustomField,
    Document,
    InnerDoc,
    Integer,
    Keyword,
    Object,
    Text,
)

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from zoom_settings import CLIENT
from zoom_shared.zoom_utils import _parse_date

VERSION_NUMBER = 1
TEMPLATE_NAME = f"{CLIENT}-zoom-v{VERSION_NUMBER}"
PATTERN = f"{TEMPLATE_NAME}-*"


class DataInput:
    alias = "zoom_input"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class FingerprintDate(CustomField):
    builtin_type = "date"

    def date(self, date, fmt) -> str:
        return _parse_date(date, fmt)


class FingerprintMeta(InnerDoc):
    """
    Key Join Signature throughout Indexes
    """

    bucket = Keyword()
    client = Keyword()
    key = Keyword()
    key_audio = Keyword()
    key_cdr = Keyword()
    key_transcript = Keyword()
    processed_time = FingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    time = FingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    tenant = Keyword()
    type = Keyword()
    type_transcription = Keyword()
    aws_lambda_id = Keyword()
    schema = Integer(Schema.version)


class PersonaID(InnerDoc):
    """
    Metadata of Person
    """

    email_address = Text(fields={"keyword": Keyword()})
    alternative_id = Text(fields={"keyword": Keyword()})
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    domain = Text(fields={"keyword": Keyword()})
    tel_number = Text(fields={"keyword": Keyword()})


class Phrase(InnerDoc):
    """
    The conversational individual block
    """

    start_time = Float()
    end_time = Float()
    text = Text(analyzer="english", term_vector="with_positions_offsets")
    speaker = Keyword()


class BodyDetail(InnerDoc):
    phrases = Object(Phrase)
    has_body = Boolean()


class ZOOM(Document):
    """
    ZOOM MASTER DOCUMENT
    """

    to = Text(fields={"keyword": Keyword()})
    to_detail = Object(PersonaID, multi=True)
    from_ = Text(fields={"keyword": Keyword()})
    from_detail = Object(PersonaID)
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    body_detail = Object(BodyDetail)
    date = FingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    fingerprint = Object(FingerprintMeta)

    class Index:
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1,
        }
        aliases = {"ips_data_zoom": {}}
