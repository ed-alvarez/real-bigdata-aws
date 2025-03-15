from logging import DEBUG, INFO, basicConfig, getLogger
from os import getenv

from boto3 import client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ENTITY_CONFIDENCE_THRESHOLD = 0.5
KEY_PHRASES_CONFIDENCE_THRESHOLD = 0.7
entityTypes = ["COMMERCIAL_ITEM", "EVENT", "LOCATION", "ORGANIZATION", "TITLE", "PERSON"]

# Log level
basicConfig()
logger = getLogger()
if getenv("LOG_LEVEL") == "DEBUG":
    logger.setLevel(DEBUG)
else:
    logger.setLevel(INFO)


class enrichText:
    """use the AWS comprehend service to
    - detect the enrichedLanguage
    - detect the enrichedSentiment
    - detect key phrases
    - detect enrichedEntities
    Can operate on each item of dicovery or on all of them at once
    defaults to 'en' as enrichedLanguage which is modified if the translate method is called
    The target enrichedLanguage is
    """

    def __init__(self):
        self._comprehend_client = client("comprehend")
        self._translate_client = client("translate")
        self._text = str("")
        self._language = list([])
        self._target_language_code = str("en")
        self._source_language_code = str("en")
        self._entities = list([])
        self._key_phrases = list([])
        self._sentiment = dict([("Sentiment", ""), ("SentimentScore", dict())])
        self._translated_text = str("")
        self._vader_sentiment = dict([("Sentiment", ""), ("SentimentScore", dict())])
        self._translated_entities = list([])
        self._translated_key_phrases = list([])
        self._translated_sentiment = dict([("Sentiment", ""), ("SentimentScore", dict())])

    @property
    def textToEnrich(self):
        return self._text

    @textToEnrich.setter
    def textToEnrich(self, value):
        self._text = value

    @property
    def sourceLanguageCode(self):
        return self._source_language_code

    @sourceLanguageCode.setter
    def sourceLanguageCode(self, value):
        if value in [
            "en-US",
            "es-US",
            "en-AU",
            "fr-CA",
            "en-GB",
            "de-DE",
            "pt-BR",
            "fr-FR",
            "it-IT",
            "ko-KR",
            "es-ES",
            "en-IN",
            "hi-IN",
            "ar-SA",
            "ru-RU",
            "zh-CN",
            "nl-NL",
            "id-ID",
            "ta-IN",
            "fa-IR",
            "en-IE",
            "en-AB",
            "en-WL",
            "pt-PT",
            "te-IN",
            "tr-TR",
            "de-CH",
            "he-IL",
            "ms-MY",
            "ja-JP",
            "ar-AE",
        ]:
            self._source_language_code = value

    @property
    def targetLanguage(self):
        return self._target_language_code

    @targetLanguage.setter
    def targetLanguage(self, value):
        self._target_language_code = value

    @property
    def enrichedLanguage(self):
        return self._language

    @property
    def enrichedEntities(self):
        return self._entities

    @property
    def enrichedKeyPhrases(self):
        return self._key_phrases

    @property
    def enrichedSentiment(self):
        return self._sentiment

    @property
    def translatedText(self):
        return self._translated_text

    @property
    def vaderSentiment(self):
        return self._vader_sentiment

    @property
    def translatedEntities(self):
        return self._translated_entities

    @property
    def translatedKeyPhrases(self):
        return self._translated_key_phrases

    @property
    def translatedSentiment(self):
        return self._translated_sentiment

    def _reset_variables(self):
        self._comprehend_client = client("comprehend")
        self._translate_client = client("translate")
        self._text = str("")
        self._language = list([])
        self._target_language_code = str("en")
        self._source_language_code = str("en")
        self._entities = list([])
        self._key_phrases = list([])
        self._sentiment = dict([("Sentiment", ""), ("SentimentScore", dict())])
        self._translated_text = str("")
        self._vader_sentiment = dict()
        self._translated_entities = list([])
        self._translated_key_phrases = list([])
        self._translated_sentiment = dict([("Sentiment", ""), ("SentimentScore", dict())])

    def enrichText(self):
        self._detect_language()
        self.detect_sentiment()
        self.detect_entities()
        self.detect_key_phrases()
        self.detect_vader_sentiment()

    def _detect_language(self):
        """Run detect language to use the AWS language detection"""
        language = str()
        language = self._comprehend_client.detect_dominant_language(Text=self._text)
        self._language = language["Languages"]
        self._source_language_code = language["Languages"][0]["LanguageCode"]
        return language["Languages"]

    def detect_entities(self, alt_text=None):
        entities = list([])
        text = str()
        if alt_text:
            text = alt_text
        else:
            text = self._text

        if self._source_language_code in ["en", "es", "fr", "de", "it", "pt", "ar", "hi", "ja", "ko", "zh", "zh-TW"]:
            response = self._comprehend_client.detect_entities(Text=text, LanguageCode=self._source_language_code)

            for i in range(len(response["Entities"])):
                entity = response["Entities"][i]
                if entity["Type"] in entityTypes and entity["Score"] > ENTITY_CONFIDENCE_THRESHOLD:
                    entities.append(entity["Text"])

            if not alt_text:
                self._entities = entities
        return entities

    def detect_key_phrases(self, alt_text=None):
        key_phrases = list()
        text = str()

        if alt_text:
            text = alt_text
        else:
            text = self._text

        if self._source_language_code in ["en", "es", "fr", "de", "it", "pt", "ar", "hi", "ja", "ko", "zh", "zh-TW"]:
            response = self._comprehend_client.detect_key_phrases(Text=text, LanguageCode=self._source_language_code)

        for i in range(len(response["KeyPhrases"])):
            keyphrase = response["KeyPhrases"][i]
            if keyphrase["Score"] > KEY_PHRASES_CONFIDENCE_THRESHOLD:
                key_phrases.append(keyphrase["Text"])
        if not alt_text:
            self._key_phrases = key_phrases
        return key_phrases

    def detect_sentiment(self, alt_text=None):
        sentiment = dict()
        text = str()
        if alt_text:
            text = alt_text
        else:
            text = self._text

        if self._source_language_code in ["en", "es", "fr", "de", "it", "pt", "ar", "hi", "ja", "ko", "zh", "zh-TW"]:
            sentiment = self._comprehend_client.detect_sentiment(Text=text, LanguageCode=self._source_language_code)
        else:
            sentiment["Sentiment"] = "XXX Invalid Language XXX"
        if not alt_text:
            self._sentiment = sentiment

        return sentiment

    def summary_sentiment(self, compound_score):
        summary = str()
        if compound_score >= 0.5:
            return "POSITIVE"
        if compound_score >= -0.5 and compound_score < 0.5:
            return "NEUTRAL"
        if compound_score <= -0.5:
            return "NEGATIVE"

    def detect_vader_sentiment(self, alt_text=None):
        # Vader Sentiment only works on english text so a translation will be forced if the source is not english

        vader_sentiment = dict()
        text = str()
        if alt_text:
            text = alt_text
        else:
            if self._source_language_code == "en":
                text = self._text
            else:
                text = self.translate_text(run_all_detections=False)

        analyzer = SentimentIntensityAnalyzer()
        result = analyzer.polarity_scores(text)

        # Make the results in AWS format
        score = dict(
            [("Positive", result["pos"]), ("Negative", result["neg"]), ("Neutral", result["neu"]), ("Mixed", result["compound"])]
        )

        vader_sentiment["Sentiment"] = self.summary_sentiment(result["compound"])
        vader_sentiment["SentimentScore"] = score

        if not alt_text:
            self._vader_sentiment = vader_sentiment

        return vader_sentiment

    def translate_text(self, run_all_detections=True):
        """Translate text 7 populate translated atributes
        run_all_detections=False will just translate"""

        translated_text = str()

        if self._source_language_code == "en":
            # if the source language hasn't been set then automatically detect language
            self._detect_language()

        if self._source_language_code == "en":
            # if after detection the language is still the same then don't translate
            self._translated_text = ""
        else:
            # If the language is different do the translation and populate the Detections
            response = self._translate_client.translate_text(
                Text=self._text, SourceLanguageCode=self._source_language_code, TargetLanguageCode=self._target_language_code
            )
            translated_text = response["TranslatedText"]
            self._translated_text = translated_text

            if run_all_detections:
                self._translated_entities = self.detect_entities(alt_text=translated_text)
                self._translated_key_phrases = self.detect_key_phrases(alt_text=translated_text)
                self._translated_sentiment = self.detect_sentiment(alt_text=translated_text)
                self._vader_sentiment = self.detect_vader_sentiment(alt_text=translated_text)

        return translated_text


if __name__ == "__main__":
    import pprint

    enrich_text = enrichText()
    # enrich_text.textToEnrich = "Nous venons vers vous en notre qualité de syndic de la résidence LE BELVEDERE 1056 route du Belvédère à COURCHEVEL MORIOND - SAINT BON TARENTAISE " \
    #                               "Suite aux relevés d’eau effectués par la société IDEX, il apparait qu’une intervention pouvant donner lieu au remplacement de vos compteurs devra être effectuée par le prestataire." \
    #                               "Nous vous soumettons ci-après plusieurs dates parmi lesquels nous vous demandons de bien vouloir bloquer un créneau horaire entre 8 heures et midi ou entre 13 heures 30 et 17.00 :"

    enrich_text.textToEnrich = "So what you are saying is that each client does not have their own separate Mimecast tenant? Instead they use the RFA tenant and you permission/separate access to the data when they want to search the archive – or do you not permit them searching the archive and that’s why some of your clients buy GlobalRelay?"

    enrich_text.enrichText()
    # enrich_text.translate_text()

    pprint.pprint(enrich_text)
