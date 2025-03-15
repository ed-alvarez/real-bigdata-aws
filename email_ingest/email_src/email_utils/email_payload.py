import logging

import email_settings
import lxml
from bs4 import BeautifulSoup
from email_helpers.es_email_index_v2 import EMAIL, BodyDetail, SubjectDetail
from email_helpers.ips_tools import convert_size
from email_helpers.log_messages import warning
from email_reply_parser import EmailReplyParser
from icalendar import Calendar
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

log = logging.getLogger()


class EmailPayload:
    def __init__(self):
        self._email_msg = None
        self._payload = EMAIL()

    @property
    def emailMessage(self):
        return self._email_msg

    @emailMessage.setter
    def emailMessage(self, value):
        self._email_msg = value

    @property
    def emailPayload(self):
        return self._payload

    @emailPayload.setter
    def emailPayload(self, value):
        self._payload = value

    def parse_calendar_address(self, addresses):
        """
        Take an iCalendar single or multiple addressee list and create a string response of only the email part
        the format seems to be MAILTO:james@ip-sentinel.com
        """
        if type(addresses) is list:
            new_addresses = []
            for address in addresses:
                email = address.split(":")[-1]
                new_addresses.append(email)
            formatted_address = ", ".join(new_addresses)
            return formatted_address
        else:
            email = addresses.split(":")[-1]
            return email

    def process_icalendar(self, calendar_part):
        try:
            calendar_item = Calendar.from_ical(st=calendar_part)
        except (ValueError, IndexError, KeyError) as ex:
            warning_msg = warning["unable_to_decode_iCal"].format(ex)
            log.warning(warning_msg)
            return warning_msg

        event = {}
        for item in calendar_item.walk("VEVENT"):
            if "ORGANIZER" in item:
                if item["ORGANIZER"]:
                    event["organiser"] = self.parse_calendar_address(item["ORGANIZER"])
            if "ATTENDEE" in item:
                if item["ATTENDEE"]:
                    event["attendees"] = self.parse_calendar_address(item["ATTENDEE"])
            if "SUMMARY" in item:
                if item["SUMMARY"]:
                    event["summary"] = item["SUMMARY"]
            if "DESCRIPTION" in item:
                if item["DESCRIPTION"]:
                    event["description"] = item["DESCRIPTION"]
            if "LOCATION" in item:
                if item["LOCATION"]:
                    event["location"] = item["LOCATION"]
            if "DTSTART" in item:
                if item["DTSTART"]:
                    event["start"] = item.decoded("DTSTART")
            if "DTEND" in item:
                if item["DTEND"]:
                    event["end"] = item.decoded("DTEND")

        event_str = "\r\n".join([" : ".join([key, str(val)]) for key, val in event.items()])
        return event_str

    def convert_html_body_to_plain(self, raw_body_html):

        try:
            soup = BeautifulSoup(raw_body_html, "lxml")
        except (ValueError, IndexError, KeyError) as ex:
            warning_msg = warning["unable_to_decode_html"].format(ex)
            log.warning(warning_msg)
            return warning_msg

        output = soup.text

        # output = ''
        # blacklist = email_settings.HTML_TAGS_BLACKLIST

        # for t in text:
        #    if t.parent.name not in blacklist:
        #        output += '{} '.format(t)

        return output

    def clean_body(self, body_text):
        step_1 = body_text.lstrip()
        step_2 = step_1.replace("  ", "")
        step_3 = step_2.replace("\n\n", "")
        step_4 = step_3.replace("\n ", "")
        step_5 = step_4.replace("\t", "")
        step_6 = step_5.replace("\n \n", "\n")
        clean_text = step_5.rstrip()
        return clean_text

    def generate_subject_details(self, subject):
        subject_detail = SubjectDetail()
        subject_detail.has_subject = False
        if subject:
            sid = SentimentIntensityAnalyzer()
            subject_detail.has_subject = True
            subject_detail.subject_sentiment = sid.polarity_scores(subject)
        return subject_detail

    def get_payload_from_email(self, content_type):
        complete_payload = str("")
        if isinstance(self._email_msg["payloads"], list):
            for individual_payload in self._email_msg["payloads"]:
                if isinstance(individual_payload["payloads"], list):
                    log.debug(f"WARNING: Multiple payloads so maybe a Non Delivery Report")
                    pass
                else:
                    if "content-type" in individual_payload["headers"]:
                        if content_type in individual_payload["headers"]["content-type"]:
                            payload = individual_payload["payloads"]
                            if len(payload) >> 0:
                                complete_payload += payload
                    else:
                        log.warning(f"WARNING: Content-Type missing in individual payload")
        else:
            if "content-type" in self._email_msg["headers"]:
                if content_type in self._email_msg["headers"]["content-type"]:
                    complete_payload = self._email_msg["payloads"]
                else:
                    log.warning(f"WARNING: Content-Type missing in the single payload")

        return complete_payload

    def construct_body_content(self):
        raw_body_plain = ""

        # Get Text & HTML parts of Payload
        raw_body_plain = self.get_payload_from_email(content_type="text/plain")
        raw_body_html = self.get_payload_from_email(content_type="text/html")
        raw_body_calendar = self.get_payload_from_email(content_type="text/calendar")

        if raw_body_calendar:
            raw_body_plain = self.process_icalendar(calendar_part=raw_body_calendar)

        parsed_email_body = ""

        if raw_body_html and not raw_body_plain:
            dirty_body = self.convert_html_body_to_plain(raw_body_html)
            parsed_email_body = self.clean_body(body_text=dirty_body)
        else:
            parsed_email_body = raw_body_plain
        return parsed_email_body

    def generate_body_detail(self, email_body, full_email_body):
        body_detail = BodyDetail()
        body_detail.has_body = False
        if email_body:
            body_detail.body_size = len(email_body)
            if body_detail.body_size <= email_settings.SENTIMENT_MAXIMUM_SIZE_TO_ANALYSE:
                sid = SentimentIntensityAnalyzer()
                body_detail.body_sentiment = sid.polarity_scores(email_body)
            else:
                log.warning(f"Email Body Text is too big for Sentiment Analysis as it's {convert_size(body_detail.body_size)}")
            body_detail.has_body = True
        if full_email_body:
            body_detail.full_body = full_email_body

        return body_detail

    def populate_payload(self):

        # Body Processing
        log.debug("Body Processing")
        full_email_body = str("")
        body_content = str("")

        email_body_content = self.construct_body_content()

        if len(email_body_content) <= email_settings.BODY_PARSER_MAXIMUM_SIZE_TO_ANALYSE:
            individual_email = EmailReplyParser.parse_reply(email_body_content)
        else:
            read_size = convert_size(len(email_body_content))
            log.warning(f"Email Body is too big to Parse for reply chains {read_size}")
            individual_email = email_body_content

        # Heuristically if the body is too short it mans the parsing has gone wrong so include the full email.
        # this can happen if the first entry is [External Email]
        # The downside is that the disclaimer is included
        if len(individual_email) < 20:
            body_content = email_body_content
        elif individual_email:
            body_content = individual_email
        else:
            body_content = email_body_content

        self._payload.body = body_content
        self._payload.body_detail = self.generate_body_detail(email_body=body_content, full_email_body=email_body_content)

        # Subject Processing
        if "subject" in self._email_msg["headers"]:
            if isinstance(self._email_msg["headers"]["subject"], str):
                # subject = decode_from_utf8(self._email_msg["headers"]['subject'])
                self._payload.subject = self._email_msg["headers"]["subject"]
                self._payload.subject_detail = self.generate_subject_details(subject=self._payload.subject)


if __name__ == "__main__":
    import pprint

    from email_ingest.email_src.email_utils.generate_email_obj import parseMIME

    def mime_file(file_id):
        mime_file_to_open = open("/Users/hogbinj/PycharmProjects/emailStep/email_tests/sample_emails/" + str(file_id), "rb")
        msg = mime_file_to_open.read()
        return msg

    def email_object(file_id):
        email = parseMIME()
        email.byteMail = mime_file(file_id=file_id)
        email.process_message()
        return email

    def test_simple_MIME():
        mime_file_id = "valeur_calendar"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        pprint.pprint(payload.emailPayload)

    def test_encoded_MIME():
        mime_file_id = "b64encodedmime"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        pprint.pprint(payload.emailPayload)

    def test_complex_meeting():
        mime_file_id = "complex_meeting"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        pprint.pprint(payload.emailPayload)

    def test_single_word_body():
        mime_file_id = "single_word_body"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        pprint.pprint(payload.emailPayload)

    def test_missing_body_due_to_external_email_warning():
        mime_file_id = "owl_rock_body_missing"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        pprint.pprint(payload.emailPayload)

    test_missing_body_due_to_external_email_warning()
