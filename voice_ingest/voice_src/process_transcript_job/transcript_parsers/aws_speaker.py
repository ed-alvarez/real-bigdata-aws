from json import loads
from logging import basicConfig, getLogger

from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import BodyDetail
from voice_src.process_transcript_job.transcript_parsers.aws_transcript_tools import (
    _get_speaker_label,
    _parse_speaker_segments,
    _phrase,
    _populate_phrase,
)

basicConfig()
logger = getLogger()


class awsSpeaker:
    def __init__(self):
        self._raw_json = str()
        self._body_detail = list()

    @property
    def rawJSON(self):
        return self._raw_json

    @rawJSON.setter
    def rawJSON(self, value):
        self._raw_json = loads(value)

    @property
    def fullTranscript(self):
        return self._raw_json["results"]["transcripts"][0]["transcript"]

    @property
    def bodyDetail(self):
        return self._body_detail

    def process_speaker(self):
        # comprehend_chunks, phrases = self.chunk_up_transcript(results = self.cdr['results'],custom_vocabs=None)
        body_detail = self._analyse_by_paragaraph()
        self._body_detail = body_detail
        return body_detail

    def _analyse_by_paragaraph(self):
        results = self._raw_json["results"]
        items = results["items"]
        body_detail = BodyDetail()
        body_detail.has_body = False
        body_detail.phrases = list()
        mapping = ""
        paragraphGap = 0.5
        newParagraph = False
        hasSpeakerLabels = False
        speakerMapping = []

        # Create a mapping of the transitions from one speaker to another
        if "speaker_labels" in results:
            speakerMapping = _parse_speaker_segments(results)
            hasSpeakerLabels = True
        else:
            speakerLabel = "spk_0"

        speakerIndex = 0

        # Repeat the loop for each item (word and punctuation)
        # The transcription will be broken out into a number of sections that are referred to
        # below as phrase. The phrase is the unit text that is stored in the
        # elasticsearch index. It is broken out by punctionation, speaker changes, a long pause
        # in the audio, or overall length

        for i, item in enumerate(items):
            if i == 0:
                # Set Up in loop 0
                item_phrase = _phrase()
                item_phrase.prev_speaker = "spk_0"
                item_phrase.prev_end_time = float(item["start_time"])
                item_phrase.prev_start_time = float(item["start_time"])

            if item["type"] == "punctuation":
                if item["alternatives"][0]["content"] == ".":
                    newParagraph = True
                # Always assume the first guess is right.
                item_phrase.contents += item["alternatives"][0]["content"]
                continue

            # gap refers to the amount of time between spoken words
            item_phrase.gap = float(item["start_time"]) - item_phrase.prev_end_time

            if hasSpeakerLabels:
                speakerLabel = _get_speaker_label(speakerMapping, float(item["start_time"]))

            # Change paragraphs if the speaker changes
            if speakerLabel != item_phrase.prev_speaker:
                newParagraph = True
                item_phrase.reason = "Speaker Change from " + item_phrase.prev_speaker + " to " + speakerLabel
            # the gap exceeds a preset threshold
            elif item_phrase.gap > paragraphGap:
                newParagraph = True
                item_phrase.reason = "Time gap"
            # There are over 4900 words (The limit for comprehend is 5000)
            elif len(item_phrase.contents) > 4900:
                newParagraph = True
                item_phrase.reason = "Long paragraph"
            else:
                newParagraph = False

            if i > 0 and newParagraph:
                enriched_phrase = _populate_phrase(item_phrase=item_phrase)
                # append the block of text to the array.
                body_detail.phrases.append(enriched_phrase)
                body_detail.has_body = True

                # Reset the contents and the time mapping
                item_phrase.contents = ""
                item_phrase.prev_end_time = float(item["start_time"])
                item_phrase.prev_start_time = float(item["start_time"])
                newParagraph = False

            else:
                item_phrase.prev_end_time = float(item["end_time"])

            item_phrase.prev_speaker = speakerLabel

            # If the contents are not empty, prepend a space
            if item_phrase.contents != "":
                item_phrase.contents += " "

            # Always assume the first guess is right.
            word = item["alternatives"][0]["content"]

            # Map the custom words back to their original text
            for key in mapping:
                val = mapping[key]
                word = word.replace(key, val)

            item_phrase.contents += word

        # Handle the last phrase
        enriched_phrase = _populate_phrase(item_phrase=item_phrase)
        # append the block of text to the array.
        body_detail.phrases.append(enriched_phrase)
        body_detail.has_body = True

        return body_detail
