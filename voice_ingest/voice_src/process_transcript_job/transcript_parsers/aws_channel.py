from json import loads
from logging import basicConfig, getLogger
from operator import itemgetter

from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import BodyDetail
from voice_src.process_transcript_job.transcript_parsers.aws_transcript_tools import (
    _phrase,
    _populate_phrase,
)

commonDict = {"i": "I"}

basicConfig()
logger = getLogger()


class awsChannel:
    def __init__(self):
        self._raw_json = str()
        self._body_detail = BodyDetail()

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

    def process_channel(self):
        channels = self._raw_json["results"]["channel_labels"]["channels"]
        body_detail = BodyDetail()

        for i, channel in enumerate(channels):
            channel_phrase = dict()
            result = self._analyse_by_paragaraph(channel_items=channel["items"], channel_name=channel["channel_label"])
            if i == 0:
                body_detail = result
            else:
                body_detail = self._merge_and_sort_body_detail(body_detail, result)

        self._body_detail = body_detail

        return body_detail

    def _merge_and_sort_body_detail(self, body_detail, result):
        new_body_detail = BodyDetail()
        for phrase in result.phrases:
            body_detail.phrases.append(phrase)

        new_body_detail.phrases = sorted(body_detail.phrases, key=itemgetter("start_time"))
        new_body_detail.has_body = body_detail.has_body

        return new_body_detail

    def _analyse_by_paragaraph(self, channel_items, channel_name):
        body_detail = BodyDetail()
        body_detail.has_body = False
        mapping = ""
        paragraphGap = 0.5
        newParagraph = False

        # Repeat the loop for each item (word and punctuation)
        # The transcription will be broken out into a number of sections that are referred to
        # below as phrase. The phrase is the unit text that is stored in the
        # elasticsearch index. It is broken out by punctionation,  a long pause
        # in the audio, or overall length

        for i, item in enumerate(channel_items):
            if i == 0:
                # Set Up in loop 0
                item_phrase = _phrase()
                item_phrase.prev_speaker = channel_name
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

            # the gap exceeds a preset threshold
            if item_phrase.gap > paragraphGap:
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

    def convertPositionToTime(offset, timedata):
        timeposition = ""
        for i in range(len(timedata)):
            if int(timedata[i]["position"]) <= int(offset):
                timeposition = timedata[i]["startTime"]

        return timeposition
