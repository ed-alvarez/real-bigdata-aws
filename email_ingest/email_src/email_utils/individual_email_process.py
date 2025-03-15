import logging

from email_helpers.es_email_index_v2 import EMAIL
from email_src.attachment_parser.route_attachment import EmailAttachments
from email_src.email_utils.email_envelope import EmailEnvelope
from email_src.email_utils.email_payload import EmailPayload
from email_src.email_utils.generate_email_obj import parseMIME

log = logging.getLogger()


class EMAILObject:
    def __init__(self):
        log.debug("Initialising Email Object...")
        self._byte_mail = None
        self._email_obj = None
        self._es_email_obj = EMAIL()
        self._attachments = None
        self._parsing_message_byt = None

    @property
    def byteMail(self):
        return self._byte_mail

    @byteMail.setter
    def byteMail(self, byte_mail):
        self._byte_mail = byte_mail

    @property
    def email(self):
        return self._es_email_obj

    def process_message(self):
        """
        Process the properties, body and attachments retrieved from s3.
        using https://pypi.org/project/mail-parser/ and the python SMTTP library

        the method


        Return : True or False for if there are any errors and any error if one occurred.  Will ony be populated if
        success False.
        """
        log.debug("Parsing message...")

        # Create email objects from the s3 Byte string
        mime_to_email = parseMIME()
        mime_to_email.byteMail = self._byte_mail
        mime_to_email.process_message()
        self._email_obj = mime_to_email.parsedMIME

        # Process envelope attributes, To, From, CC, Message ID, Date
        # Returns a partially populated ES EMAIL object
        email_envelope = EmailEnvelope()
        email_envelope.emailMessage = self._email_obj
        email_envelope.emailEnvelope = self._es_email_obj
        email_envelope.populate_envelope()
        self._es_email_obj = email_envelope.emailEnvelope

        # Process Payload attributes, Subject and Body
        # Discovers if body is Calendar item and decodes that
        email_payload = EmailPayload()
        email_payload.emailMessage = self._email_obj
        email_payload.emailPayload = self._es_email_obj
        email_payload.populate_payload()
        self._es_email_obj = email_payload.emailPayload

        # Process Any Attachments
        email_attachments = EmailAttachments()
        email_attachments.emailMessage = self._email_obj
        email_attachments.emailAttachments = self._es_email_obj
        email_attachments.populate_attachments()
        self._es_email_obj = email_attachments.emailAttachments

        return True


if __name__ == "__main__":
    import pprint

    def mime_file(file_id):
        mime_file_to_open = open("/Users/hogbinj/PycharmProjects/emailStep/email_tests/sample_emails/" + str(file_id), "rb")
        msg = mime_file_to_open.read()
        return msg

    def email_object(file_id):
        email = EMAILObject()
        email.byteMail = mime_file(file_id=file_id)
        try:
            email.process_message()
        except Exception as ex:
            log.exception(ex)
        return email.email

    def test_process_email():
        mime_file_id = "i0orr65o0hfsducsgbkg0bf1pcl669ehngtqn581"
        output = email_object(file_id=mime_file_id)
        pprint.pprint(output)

    test_process_email()
