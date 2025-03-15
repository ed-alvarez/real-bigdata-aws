from voice_settings import ENRICH_PHRASES
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import (
    Phrase,
    Sentiment,
)
from voice_src.process_transcript_job.enrich_text import enrichText


class _phrase:
    def __init__(self):
        self.prev_speaker = str("")
        self.gap = str("")
        self.prev_start_time = str("")
        self.prev_end_time = str("")
        self.contents = str("")
        self.reason = str("")


def _parse_speaker_segments(results):
    speaker_labels = results["speaker_labels"]["segments"]
    speaker_segments = []
    for label in speaker_labels:
        segment = dict()
        segment["startTime"] = float(label["start_time"])
        segment["endTime"] = float(label["end_time"])
        segment["speakerLabel"] = label["speaker_label"]
        speaker_segments.append(segment)
    return speaker_segments


def _get_speaker_label(speaker_segments, start_time):
    for segment in speaker_segments:
        if segment["startTime"] <= start_time < segment["endTime"]:
            return segment["speakerLabel"]
    return None


def _get_time_code(seconds):
    # t_hund = int(seconds % 1 * 1000)
    # t_seconds = int(seconds)
    # t_secs = ((float(t_seconds) / 60) % 1) * 60
    # t_mins = int(t_seconds / 60)
    # return str("%02d:%02d:%02d,%03d" % (00, t_mins, int(t_secs), t_hund))

    return round(seconds, 2)


def _parse_sentiment(enriched_text):
    sentiment_obj = Sentiment()
    enriched_text.detect_vader_sentiment()
    sentiment = enriched_text.vaderSentiment
    sentiment_obj.neg = sentiment["SentimentScore"]["Negative"]
    sentiment_obj.neu = sentiment["SentimentScore"]["Neutral"]
    sentiment_obj.pos = sentiment["SentimentScore"]["Positive"]
    sentiment_obj.compound = sentiment["SentimentScore"]["Mixed"]
    sentiment_obj.summary = sentiment["Sentiment"]

    return sentiment_obj


def _populate_phrase(item_phrase):
    enrich_text = enrichText()
    enrich_text.textToEnrich = item_phrase.contents
    phrase = Phrase()
    phrase.speaker = item_phrase.prev_speaker
    phrase.gap = _get_time_code(item_phrase.gap)
    phrase.start_time = _get_time_code(item_phrase.prev_start_time)
    phrase.end_time = _get_time_code(item_phrase.prev_end_time)
    phrase.text = item_phrase.contents
    phrase.reason = item_phrase.reason
    if ENRICH_PHRASES:
        enrich_text.detect_key_phrases()
        enrich_text.detect_entities()
        phrase.entities = enrich_text.enrichedEntities
        phrase.key_phrases = enrich_text.enrichedKeyPhrases

    phrase.sentiment = _parse_sentiment(enriched_text=enrich_text)

    return phrase
