"""
Utility lambdas
"""
import json
import logging
import re
import sys
from datetime import date, datetime, timedelta
from functools import wraps
from time import time
from typing import Dict, Optional

from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters


def my_import(name):
    """Function converts a string based import into a module object, used for
    dynamically importing modules from config.

    Parameters
    ----------
    :str: `str`
        A string name of the module to import

    Returns
    -------
    :obj: `module`
        A module object converted from the string.

    """
    components = name.split(".")
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_date_based_folder():
    """Function to return the folder path based on todays date.

    Parameters
    ----------
    None

    Returns
    -------
    str: `str`
        A string that contains the current date YYYY/MM/DD

    """
    int_date = str(datetime.utcnow().date())
    return int_date.replace("-", "/")


def check_new_day(folder_date):
    """Function that checks what the current date is and determines if a new
    folder is required to be made"""
    return datetime.utcnow().date() != folder_date


def generate_event(file_name, datetime=datetime):
    """Function to generate json with a timestamp and filname headers."""
    return json.dumps(
        {
            "timestamp": datetime.now().isoformat(),
            "filename": file_name,
        },
    )


def chop_end_of_string(str_input, str_remove):
    """Function that strips the supplied str_remove from the end of the input
    string

    Parameters
    ----------
    str_input: `str`
                A string to be chopped
    str_remove: `str`
                The string to be removed from the end of the input

    Returns
    -------
    str: `str`
        A string that contains the new string

    """
    if str_input.endswith(str_remove):
        return str_input[: -len(str_remove)]
    return str_input


def date_within_range(file_date):
    today = date.today()
    margin = timedelta(days=21)
    earliest_date = today - margin
    latest_date = today + margin

    file_date_dt = datetime.strptime(file_date, "%Y-%m-%d").date()

    if earliest_date <= file_date_dt <= latest_date:
        return True

    return False


def get_date_from_file_path(file_path, dt_range_check=False):
    date_str = file_path.split(".")[2]
    if len(date_str) != 6:
        raise ValueError(f"BBG File date of {date_str} is the wrong length")
    try:
        file_date = datetime.strptime(date_str, "%y%m%d").strftime("%Y-%m-%d")  # valid datetime
    except Exception as ex:
        raise ValueError(f"BBG File date of {date_str} cannot be parsed due to {ex}")

    if dt_range_check and not date_within_range(file_date):
        raise ValueError(f"BBG File date not within 21 days of todays date")

    return file_date


def get_date_from_file_path_depreciated(file_path):
    """Function that attempts to intelligently determine a date from a file path"""
    Y = ("%Y", r"20\d{2}")
    y = ("%y", r"\d{2}")
    m = ("%m", r"\d{1,2}")
    d = ("%d", r"\d{1,2}")
    presufs = [r"/", r"\."]  # prefix and suffix priorities (before/after date separator)
    delims = ["-", ""]  # delimiter priorities (inter-date separator)
    formats = [
        list(zip(Y, m, d)),  # 4 digit year format (uppercase Y)
        list(zip(y, m, d)),  # 2 digit year format (lowercase y)
    ]

    for f in formats:
        for d in delims:
            for p in presufs:
                date_format = d.join(f[0])
                re_pattern = p + "(" + d.join(f[1]) + ")" + p
                for m in re.finditer(re_pattern, file_path):
                    date_str = m.group(1)
                    try:
                        return datetime.strptime(date_str, date_format).strftime("%Y-%m-%d")  # valid datetime
                    except Exception:
                        pass


def timing(f):
    """
    Provides a timer decorator that issues a log line with a time
    """
    log = logging.getLogger()

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        log_message = {}
        log_message["tag"] = "Timing"
        log_message["text"] = "func:%r took: %2.4f sec" % (f.__name__, te - ts)
        log.info(log_message)
        return result

    return wrap


def human_readable_size(size, decimal_places=2):
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def _webvtt_to_list(string_vtt: str) -> list:
    splitted_webvtt = string_vtt.split("\r\n\r\n")
    splitted_webvtt.pop(0)
    splitted_webvtt.pop(len(splitted_webvtt) - 1)
    return splitted_webvtt


def parse_each_phrase(vtt_phrase: str) -> Dict:
    content_phrase: Optional[str] = None
    text: str
    speaker: str
    phrase: str = vtt_phrase.replace("\n", "").replace("\t", "").replace("-->", "|")

    parsed_phrase: list = phrase.split("\r")

    if len(parsed_phrase) == 2:
        # Format 1

        start_end_date: str = parsed_phrase[0]
        start_end_date: str = start_end_date.split("|")
        start_ts: str = start_end_date[0].replace(" ", "")
        end_ts: str = start_end_date[1].replace(" ", "")

        speaker: str = "Unknown"
        text: str = parsed_phrase[1]

    else:
        # Format 2

        start_end_date: str = parsed_phrase[1]
        start_end_date: str = start_end_date.split("|")
        start_ts: str = start_end_date[0].replace(" ", "")
        end_ts: str = start_end_date[1].replace(" ", "")

        speaker_text: str = parsed_phrase[2]
        try:
            if speaker_text.split(":"):
                speaker: str = speaker_text.split(":")[0]
                text: str = speaker_text.split(": ")[1].replace("'", "")
        except:
            speaker: str = "Unknown"
            text: str = speaker_text

    content_phrase = {
        "text": text,
        "end_ts": end_ts,
        "ts": start_ts,
        "speaker": speaker,
    }
    return content_phrase


def webvtt_parse_content(vtt: str) -> Dict:
    parsed_phrases: list = []

    list_phrases = _webvtt_to_list(string_vtt=vtt)

    parsed_phrases = [parse_each_phrase(vtt_phrase=phrase) for phrase in list_phrases]
    return {"content": parsed_phrases}


def load_ssm_secrets(obj):
    ssm_key_values = {name: getattr(obj, name) for name in dir(obj) if 'ssm' in getattr(obj, name)}
    for ssm_key in ssm_key_values:
        secret_path = f"{obj.client}/{ssm_key}"
        ssm_client = AWS_Key_Parameters(client_name=obj.tenant_name)
        if ssm_client.get_ssm_parameter(item_key=secret_path):
            setattr(obj, ssm_key, ssm_client.get_parameter_value(secret_path))
