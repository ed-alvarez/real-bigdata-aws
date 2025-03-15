"""
Handy common tools
"""
import base64
import email.header
import logging
import math
import quopri
import re

log = logging.getLogger()


def print_class(cls):
    """
    Turn items in a class to a string for printing
    """
    sb = []
    sb.append(str(cls.__class__) + ": ")
    for key in cls.__dict__:
        sb.append("{key}='{value}'".format(key=key, value=cls.__dict__[key]))
    return "\n".join(sb)


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def remove_newline_chars(text):
    "=?utf-8?Q?=5BFSP_Demo=5D:_Casper_Blom_publishe?=\r\n\t=?utf-8?Q?d_a_company_note_about_AP_M=C3=B8ller?=\r\n\t=?utf-8?Q?_Maersk?="
    REGEX = r"([\r\n\t])"
    clean_text = re.sub(REGEX, "", text).strip()
    return clean_text


def find_codepage(text: str) -> str:
    REGEX = r"\?(.*?)\?"
    parsed = re.search(REGEX, text)
    if parsed.group(1):
        return parsed.group(1)
    else:
        return ""


def decode_from_utf8(decode):
    # code_pages = ['iso-2022-jp', 'iso-2022-jp-1','ISO-2022-JP-2','ISO-2022-JP-3','ISO-2022-JP-2004','CP932']
    # for code_page in code_pages:

    code_page = find_codepage(decode)
    if code_page:
        value = ""
        try:
            REGEX = r"=\?{}\?B\?(.*?)\?=".format(code_page.lower())
            parsed = re.findall(REGEX, decode)
            value = "".join(parsed[0])
        except AttributeError as ex:
            log.warning(f"regex did not match header text with codepage {code_page} in header: {decode}")
            pass
        except IndexError as ex:
            log.warning(f"regex did not extract any data in the header: {decode}")
            value = " "
            pass
        except Exception as ex:
            log.exception(ex)
            pass

        if value:
            try:
                decode_val = base64.b64decode(value)
                b64_val = decode_val.decode(code_page)
                # code_page_enc = b64_val.encode(code_page.lower(), "ignore")
                # subject = code_page_enc.decode(code_page.lower())
                return b64_val
            except UnicodeEncodeError as ex:
                log.exception(f"Failed to decode {decode} with {code_page}, {ex}")
                pass

        subject = "".join(
            word.decode(encoding or "utf8") if isinstance(word, bytes) else word
            for word, encoding in email.header.decode_header(decode)
        )
        return subject
    return decode


def old_decode_from_utf8(decode):
    multiple_subject = decode.split()
    lines = list()
    for line in multiple_subject:
        if "?utf-8?" in line:
            reg_exp = r"=\?.*\?="
            reg_exp_2 = r"=\?(.*?)\?="
            new_s = re.sub(reg_exp, "", line)
            new_f = re.findall(reg_exp_2, line)
            all_part = list()
            for f in new_f:
                new_g = f"=?{f}?="
                decode_line = encoded_words_to_text(new_g)
                all_part.append(decode_line)
            all_part.append(new_s)
            decode_line = "".join(all_part)
        else:
            decode_line = line
        lines.append(decode_line)
    subject = " ".join(lines)

    return subject


def encoded_words_to_text(encoded_words):
    encoded_word_regex = r"=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}="
    charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
    if encoding == "B":
        byte_string = base64.b64decode(encoded_text)
    elif encoding == "Q":
        byte_string = quopri.decodestring(encoded_text)
    return byte_string.decode(charset)


if __name__ == "__main__":
    string = "=?gb2312?B?zrq1wtDHKEFsZnJlZCBOZ2FpKQ==?= <alfred.ts.ngai@pingan.com.hk>'"
    # string = '=?iso-2022-jp?B?GyRCLWobKEJLYWl6ZW5QbGF0Zm9ybV8bJEJMXE9AOCs9cRsoQi5wZGY=?='
    result = decode_from_utf8(string)
    print(result)
