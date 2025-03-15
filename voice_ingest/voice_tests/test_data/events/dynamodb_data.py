from datetime import datetime

from dateutil.tz import tzlocal

db_data = dict()

db_data["client"] = "test"
db_data["bucket"] = "test.ips"
db_data["file_key"] = "audio/test.wav"
db_data["transcriptionJob"] = "test-test-1590501375-9349692"
db_data["transcriptionStartTime"] = datetime(2020, 5, 26, 14, 56, 22, 88000, tzinfo=tzlocal()).isoformat()
