"""
A class to route the parsing of a particular type of transcript and return the body & full_body atributes of
ES VOICE object"""

# https://github.com/aws-samples/amazon-transcribe-comprehend-podcast

from json import loads
from logging import DEBUG, INFO, basicConfig, getLogger
from os import getenv

from boto3 import client
from voice_settings import transcribeType
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE
from voice_src.process_transcript_job.transcript_parsers.aws_channel import awsChannel
from voice_src.process_transcript_job.transcript_parsers.aws_speaker import awsSpeaker

# Log level
basicConfig()
logger = getLogger()
if getenv("LOG_LEVEL") == "DEBUG":
    logger.setLevel(DEBUG)
else:
    logger.setLevel(INFO)
# Parameters

client = client("comprehend")


class RouteTranscript:
    """
    Take a raw json file and return an ES Object for body & full_body

    """

    def __init__(self, es_record=None):
        self._raw_json = str()
        self._transcribe_type = None
        self._es_Voice = es_record or VOICE()

    @property
    def rawJSON(self):
        return self._raw_json

    @rawJSON.setter
    def rawJSON(self, value):
        self._raw_json = value

    @property
    def transcribeType(self):
        return self._transcribe_type

    @transcribeType.setter
    def transcribeType(self, value):
        self._transcribe_type = value

    @property
    def esVoice(self):
        return self._es_Voice

    def parse_transcribe_file(self):
        if self._transcribe_type == transcribeType.speaker:
            parser = awsSpeaker()
            parser.rawJSON = self._raw_json
            parser.process_speaker()
            self._es_Voice.body_detail = parser.bodyDetail
            self._es_Voice.body = parser.fullTranscript
            return parser

        elif self._transcribe_type == transcribeType.channel:
            parser = awsChannel()
            parser.rawJSON = self._raw_json
            parser.process_channel()
            self._es_Voice.body_detail = parser.bodyDetail
            self._es_Voice.body = parser.fullTranscript
            return parser

        else:
            return


if __name__ == "__main__":
    import pprint

    def transcribe_file(json_transcript_file, transcript_type):
        with open(json_transcript_file, encoding="utf8", errors="ignore") as json_file:
            raw_json = json_file.read()

        json_file = loads(raw_json)
        parse_json = RouteTranscript()
        parse_json.rawJSON = raw_json
        parse_json.transcribeType = transcript_type
        parse_json.parse_transcribe_file()
        pprint.pprint(parse_json.esVoice)

    # transcribe_file(
    #    json_transcript_file = '/Users/hogbinj/PycharmProjects/voice/voice_tests/redbox/channel_ident/test-00002471-0000-0001-2018-020507414049-1593875372-227957.json',
    #    transcript_type = transcribeType.channel
    #    )

    transcribe_file(
        json_transcript_file="/voice_tests/redbox/speaker_ident/test-00002471-0000-0001-2018-020507414049-1593875822-154132.json",
        transcript_type=transcribeType.speaker,
    )
