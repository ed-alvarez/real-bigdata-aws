import datetime
import os
import pprint

from email_settings import STAGE, eventType, keyType


class PathDetail:
    """
    Work out the paths to use for each event

    As a class input
        type of event being processed
        SES has a message_id and Client_id
        S3 has bucket and Key
        Lambda has bucket and Key

    As a class output
        :input_bucket
        :input_key
        :processed_bucket
        :processed_key
        :archive_key

    SES output will be in format
        Input
        Bucket = firm.ips
        s3Key = todo.email/mime/message_id

        Output
        Bucket = firm.ips
        processed_s3Key = processed.email/yy-mm-dd/mime/message_id

    s3 output will be in the format
        Input
        Bucket = firm.ips
        s3Key  = todo.email/mime/message_id

        Bucket = firm.ips
        s3Key  = processed.email/yy-mm-dd/mime/message_id

        Bucket = todo.firm.ips
        s3Key = email/message_id

        Bucket = stash.firm.ips
        s3Key = email/yy-mm-dd/message_id

        Output - Default - no move
        as above

        Output - move
        Bucket = firm.ips
        s3Key = processed.email/yy-mm-dd/mime/message_id

    lambda output will be in the format
        Input
        Bucket = firm.ips
        s3Key  = todo.email/mime/message_id

        Bucket = firm.ips
        s3Key  = processed.email/yy-mm-dd/mime/message_id

        Bucket = todo.firm.ips
        s3Key = email/message_id

        Bucket = stash.firm.ips
        s3Key = email/yy-mm-dd/message_id

        Output - Default - no move
        as above

        Output - move
        Bucket = firm.ips
        s3Key = processed.email/yy-mm-dd/mime/message_id

    """

    def __init__(self):
        self._input_bucket = str()
        self._input_key = str()
        self._processed_bucket = str()
        self._processed_key = str()
        self._archived_key = str()
        self._level_1_folder = str()
        self._event_type = eventType
        self._move_files = False
        self._dev_mode = self.is_dev_mode()
        self._path_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    @property
    def inputBucket(self):
        return self._input_bucket

    @inputBucket.setter
    def inputBucket(self, input_bucket):
        self._input_bucket = input_bucket

    @property
    def inputKey(self):
        return self._input_key

    @inputKey.setter
    def inputKey(self, input_key):
        self._input_key = input_key

    @property
    def eventType(self):
        return self._event_type

    @eventType.setter
    def eventType(self, event_type):
        self._event_type = event_type

    @property
    def moveFiles(self):
        return self._move_files

    @moveFiles.setter
    def moveFiles(self, move_files):
        self._move_files = move_files

    @property
    def processedBucket(self):
        return self._processed_bucket

    @property
    def processedKey(self):
        return self._processed_key

    @property
    def archivedKey(self):
        return self._archived_key

    def get_level1_folder(self):
        # Remove dev part of folder if its there.  add back on the way out if required
        level_1_folder_raw = self._input_key.split("/", 1)[0]
        env_type = level_1_folder_raw.split(".", 1)
        if env_type[0] == "dev":
            self._level_1_folder = env_type[1]
        else:
            self._level_1_folder = level_1_folder_raw

    def get_file_name(self):
        file_name = self._input_key.rsplit("/")[-1]

    def discover_type_of_key(self):
        # check to discover format of address
        # todo.ips.ips/ email/                  01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81
        # stash.ips.ips/email/                  2016-11-16/njn5o4pio297hu56iga7lu4tcm2e00a0vtjfdi01
        # ips.ips/      dev.todo.email/ mime/   0007o0qlp1vaqe4oic0onrl09qnu70qmjegj23o1
        # ips.ips/      dev.processed.email/    2020-04-03/                                 mime/   tljoco51d36kcho3vnm86kolf6cdbki68vekqso1"""

        key_format = self._input_bucket.split(".", 1)[0]
        if key_format == "todo":
            self._key_type = keyType.OldTodo
        elif key_format == "stash":
            self._key_type = keyType.OldStash
        else:
            new_key_format = self._level_1_folder.split(".")[0]
            if new_key_format == "todo":
                self._key_type = keyType.NewTodo
            elif new_key_format == "processed":
                self._key_type = keyType.NewProcessed
            else:
                pass

    def set_path_date_from_email(self, date_dt):
        self._path_date = datetime.datetime.strftime(date_dt, "%Y-%m-%d")
        self.construct_paths()

    def generate_processed_bucket(self):
        if len(self._input_bucket.rsplit(".")) == 2:
            processed_bucket = self._input_bucket
        else:
            processed_bucket = self._input_bucket.split(".", 1)[1]
        return processed_bucket

    def is_dev_mode(self):
        if STAGE == "dev":
            return True
        return False

    def generate_output_key(self, destination_folder):
        level_1_dir = ("dev." if self._dev_mode else "") + destination_folder
        file_name = self._input_key.rsplit("/")[-1]
        today_date = self._path_date
        processed_key = os.path.join(level_1_dir, today_date, "mime", file_name)
        return processed_key

    def parse_data(self):
        self.get_level1_folder()
        self.discover_type_of_key()

    def construct_paths(self):
        if self._move_files or self._event_type == eventType.SES:
            self._processed_bucket = self.generate_processed_bucket()
            self._processed_key = self.generate_output_key(destination_folder="processed.email")
            self._archived_key = self.generate_output_key(destination_folder="archived.email")
        else:
            self._processed_bucket = self._input_bucket
            self._processed_key = self._input_key

    def generate_paths(self):
        self.parse_data()
        self.construct_paths()


class pathDetailSES(PathDetail):
    def __init__(self):
        PathDetail.__init__(self)
        self._message_id = str()

    @property
    def messageID(self):
        return self._message_id

    @messageID.setter
    def messageID(self, message_id):
        self._message_id = message_id

    def ses_generate_key(self):
        input_key = ("dev." if self.is_dev_mode() else "") + "todo.email/mime/" + self._message_id
        self._input_key = input_key


if __name__ == "__main__":
    file_name = "testmessageid"
    folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    def test_1():
        file_name = "testmessageid"
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        path_detail = pathDetailSES()
        path_detail.messageID = file_name
        path_detail.inputBucket = "ips.ips"
        path_detail.eventType = eventType.SES
        path_detail.ses_generate_key()
        path_detail.generate_paths()
        pprint.pprint(path_detail.processedKey)

    def test_2():

        test = dict()
        test["bucket"] = "ips.ips"
        test["key"] = "dev.processed.email/2020-04-03/mime/" + file_name
        test["ProcessedBucket"] = "ips.ips"
        test["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name

        path_detail = PathDetail()
        path_detail.inputKey = test["key"]
        path_detail.inputBucket = test["bucket"]
        path_detail.eventType = eventType.S3
        path_detail.moveFiles = False
        path_detail.generate_paths()
        pprint.pprint(path_detail.processedKey)

    test_2()
