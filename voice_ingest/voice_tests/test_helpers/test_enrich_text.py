import pytest
from voice_src.process_transcript_job.enrich_text import enrichText

english_text = "So what you are saying is that each client does not have their own separate Mimecast tenant? Instead they use the RFA tenant and you permission/separate access to the data when they want to search the archive – or do you not permit them searching the archive and that’s why some of your clients buy GlobalRelay?"
french_text = (
    "Nous venons vers vous en notre qualité de syndic de la résidence LE BELVEDERE 1056 route du Belvédère à COURCHEVEL MORIOND - SAINT BON TARENTAISE "
    "Suite aux relevés d’eau effectués par la société IDEX, il apparait qu’une intervention pouvant donner lieu au remplacement de vos compteurs devra être effectuée par le prestataire."
    "Nous vous soumettons ci-après plusieurs dates parmi lesquels nous vous demandons de bien vouloir bloquer un créneau horaire entre 8 heures et midi ou entre 13 heures 30 et 17.00 :"
)

# Class return should be in this format
def class_format(enrich_text):
    assert type(enrich_text.enrichedEntities) is list
    assert type(enrich_text.enrichedKeyPhrases) is list
    assert type(enrich_text.enrichedLanguage) is list
    assert type(enrich_text.enrichedSentiment) is dict
    assert type(enrich_text.enrichedSentiment["SentimentScore"]) is dict
    assert type(enrich_text.vaderSentiment) is dict
    assert type(enrich_text.vaderSentiment["SentimentScore"]) is dict
    assert type(enrich_text.translatedEntities) is list
    assert type(enrich_text.translatedKeyPhrases) is list
    assert type(enrich_text.translatedSentiment) is dict
    assert type(enrich_text.translatedSentiment["SentimentScore"]) is dict


@pytest.fixture()
def enrich_text():
    return enrichText()


class TestEnrichText:
    def test_no_translation(self, enrich_text):
        enrich_text.textToEnrich = english_text
        enrich_text.enrichText()

        # Test consistent class data return
        class_format(enrich_text)

        # Parameters that should be populated are
        assert len(enrich_text.enrichedEntities) > 0
        assert len(enrich_text.enrichedKeyPhrases) > 0
        assert enrich_text.enrichedSentiment["Sentiment"] != ""
        assert enrich_text.vaderSentiment["Sentiment"] != ""

        # Parameters that should not be populated aren't
        assert len(enrich_text.translatedEntities) == 0
        assert len(enrich_text.translatedKeyPhrases) == 0
        assert enrich_text.translatedSentiment["Sentiment"] == ""
        assert enrich_text.translatedText == ""

    def test_vader_no_translation(self, enrich_text):
        enrich_text.textToEnrich = french_text
        enrich_text.enrichText()
        # Test consistent class data return
        class_format(enrich_text)

        # Parameters that should be populated are
        assert len(enrich_text.enrichedEntities) > 0
        assert len(enrich_text.enrichedKeyPhrases) > 0
        assert enrich_text.enrichedSentiment["Sentiment"] != ""
        assert enrich_text.vaderSentiment["Sentiment"] != ""
        assert enrich_text.translatedText != ""

        # Parameters that should not be populated aren't
        assert len(enrich_text.translatedEntities) == 0
        assert len(enrich_text.translatedKeyPhrases) == 0
        assert enrich_text.translatedSentiment["Sentiment"] == ""

    def test_translation_with_foreign_lingo(self, enrich_text):
        enrich_text.textToEnrich = french_text
        enrich_text.enrichText()
        enrich_text.translate_text()
        # Test consistent class data return
        class_format(enrich_text)

        # Parameters that should be populated are
        assert len(enrich_text.enrichedEntities) > 0
        assert len(enrich_text.enrichedKeyPhrases) > 0
        assert enrich_text.enrichedSentiment["Sentiment"] != ""
        assert enrich_text.vaderSentiment["Sentiment"] != ""
        assert enrich_text.translatedText != ""

        # Parameters that should not be populated aren't
        assert len(enrich_text.translatedEntities) > 0
        assert len(enrich_text.translatedKeyPhrases) > 0
        assert enrich_text.translatedSentiment["Sentiment"] != ""

    def test_translation_only(self, enrich_text):
        enrich_text = enrichText()
        enrich_text.textToEnrich = french_text
        enrich_text.translate_text(run_all_detections=False)
        # Test consistent class data return
        class_format(enrich_text)

        # Parameters that should be populated are
        assert enrich_text.translatedText != ""

        # Parameters that should not be populated aren't
        assert enrich_text.vaderSentiment["Sentiment"] == ""
        assert len(enrich_text.translatedEntities) == 0
        assert len(enrich_text.translatedKeyPhrases) == 0
        assert enrich_text.translatedSentiment["Sentiment"] == ""
        assert len(enrich_text.enrichedEntities) == 0
        assert len(enrich_text.enrichedKeyPhrases) == 0
        assert enrich_text.enrichedSentiment["Sentiment"] == ""

    def test_translation(self, enrich_text):
        enrich_text = enrichText()
        enrich_text.textToEnrich = french_text
        enrich_text.translate_text()
        # Test consistent class data return
        class_format(enrich_text)

        # Parameters that should be populated are
        assert enrich_text.translatedText != ""
        assert enrich_text.vaderSentiment["Sentiment"] != ""
        assert len(enrich_text.translatedEntities) != 0
        assert len(enrich_text.translatedKeyPhrases) != 0
        assert enrich_text.translatedSentiment["Sentiment"] != ""

        # Parameters that should not be populated aren't
        assert len(enrich_text.enrichedEntities) == 0
        assert len(enrich_text.enrichedKeyPhrases) == 0
        assert enrich_text.enrichedSentiment["Sentiment"] == ""

    def test_translation_with_no_foreign_lingo(self, enrich_text):
        enrich_text = enrichText()
        enrich_text.textToEnrich = english_text
        enrich_text.enrichText()
        enrich_text.translate_text()

        # Test consistent class data return
        class_format(enrich_text)

        # Parameters that should be populated are
        assert len(enrich_text.enrichedEntities) > 0
        assert len(enrich_text.enrichedKeyPhrases) > 0
        assert enrich_text.enrichedSentiment["Sentiment"] != ""
        assert enrich_text.vaderSentiment["Sentiment"] != ""

        # Parameters that should not be populated aren't
        assert enrich_text.translatedText == ""
        assert len(enrich_text.translatedEntities) == 0
        assert len(enrich_text.translatedKeyPhrases) == 0
        assert enrich_text.translatedSentiment["Sentiment"] == ""
