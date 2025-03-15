from logging import getLogger
from os import path
from pathlib import Path, PurePosixPath

log = getLogger()


class s3File:
    def __init__(self):
        self._file_stem = str()
        self._full_file_name = str()
        self._file_ext = str()
        self._directory = str()

        self._key = str()
        self._bucket = str()
        self._client = str()

    @property
    def bucket(self):
        log.debug(f"Property - bucket = {self._bucket}")
        return self._bucket

    @property
    def key(self):
        log.debug(f"Property - key = {self._key}")
        return self._key

    @property
    def fullFileName(self):
        log.debug(f"Property - fullFileName = {self._full_file_name}")
        return self._full_file_name

    @property
    def directory(self):
        log.debug(f"Property - directory = {self._directory}")
        return self._directory

    @property
    def fileStem(self):
        log.debug(f"Property - fileStem = {self._file_stem}")
        return self._file_stem

    @property
    def fileExtension(self):
        log.debug(f"Property - fileExtension = {self._file_ext}")
        return self._file_ext

    @property
    def client(self):
        log.debug(f"Property - client = {self._client}")
        return self._client

    @staticmethod
    def _return_client_from_bucket(bucket):
        log.debug(f"Method - _return_client_from_bucket")
        client_decode = bucket.rsplit(".", 1)[0]
        if client_decode.split(".")[0] in ["todo", "stash", "archive"]:
            return client_decode.split(".")[1]
        else:
            return client_decode

    def populate(self):
        log.debug(f"Method - populate")
        self._client = self._client
        ppp = PurePosixPath(self._key)
        self._full_file_name = ppp.name
        self._directory = ppp.parent
        self._file_stem = ppp.stem
        self._file_ext = ppp.suffix


class audioFile(s3File):
    def __init__(self):
        s3File.__init__(self)


class transcriptionFile(s3File):
    def __init__(self):
        s3File.__init__(self)
        self._db_item = dict()
        self._transcript_key = str()
        self._cdr_key = str()

    @property
    def dbItem(self):
        log.debug(f"Property - dbItem = {self._db_item}")
        return self._db_item

    @dbItem.setter
    def dbItem(self, db_item):
        log.debug(f"Property SET - dbItem = {db_item}")
        self._db_item = db_item

    @property
    def transcriptKey(self):
        log.debug(f"Property - transcriptKey = {self._transcript_key}")
        return self._transcript_key

    @property
    def cdrKey(self):
        log.debug(f"Property - cdrKey = {self._cdr_key}")
        return self._cdr_key

    def generate_transcript_file_key(self, job_name):
        log.debug(f"Method - generate transcript file key - {job_name}")
        transcript_key = f"{job_name}.json"
        return transcript_key

    def generate_cdr_file_key(self, audio_file_key):
        log.debug(f"Method - generate cdr file key - {audio_file_key}")
        # cdr_key = f"{Path(audio_file_key).stem}.json"
        cdr_key = path.splitext(audio_file_key)[0] + ".json"
        return cdr_key

    def unpack_db_results(self):
        log.debug(f"Method - unpack db results")
        self._key = self._db_item["file_key"]
        self._client = self._db_item["client"]
        self._bucket = f"{self._client}.ips"
        return

    def populate(self):
        log.debug(f"Method OVERWRITE TranscriptionFile class - populate")
        self.unpack_db_results()
        super().populate()
        self._transcript_key = self.generate_transcript_file_key(self._db_item["transcriptionJob"])
        self._cdr_key = self.generate_cdr_file_key(self._key)
        return


class filesObject:
    def __init__(self):
        self._db_item = dict()

    @property
    def dbItem(self):
        return self._db_item

    @dbItem.setter
    def dbItem(self, db_item):
        self._db_item = db_item


if __name__ == "__main__":
    import pprint

    db_results = dict(
        transcriptionJob="test-test-1590662644-682567",
        bucket="test.ips",
        client="test",
        transcriptionStartTime="2020-05-28T11:44:05.415000+01:00",
        file_key="audio/test.wav",
    )

    def trancription_files():
        transcription_files = transcriptionFile()
        transcription_files.dbItem = db_results
        transcription_files.populate()
        pprint.pprint(transcription_files)
        return

    trancription_files()
