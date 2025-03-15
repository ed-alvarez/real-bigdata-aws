import unittest

from shared.shared_src import utils

CASES = [
    ("f908067.msg.200301.xml.gpg", "2020-03-01"),
    ("f908067.msg.200302.xml.gpg", "2020-03-02"),
    ("f908067.msg.200303.xml.gpg", "2020-03-03"),
    ("f908067.msg.200304.xml.gpg", "2020-03-04"),
    ("f908067.msg.200305.xml.gpg", "2020-03-05"),
    ("f908067.msg.200306.xml.gpg", "2020-03-06"),
    ("f908067.msg.200307.xml.gpg", "2020-03-07"),
    ("f908067.msg.200308.xml.gpg", "2020-03-08"),
    ("f908067.msg.200309.xml.gpg", "2020-03-09"),
    ("f908067.msg.200310.xml.gpg", "2020-03-10"),
    ("f908067.msg.200311.xml.gpg", "2020-03-11"),
    ("f908067.msg.200312.xml.gpg", "2020-03-12"),
    ("f908067.msg.200313.xml.gpg", "2020-03-13"),
    ("f908067.msg.200314.xml.gpg", "2020-03-14"),
    ("f908067.msg.200315.xml.gpg", "2020-03-15"),
    ("f908067.msg.200316.xml.gpg", "2020-03-16"),
    ("f908067.msg.200317.xml.gpg", "2020-03-17"),
    ("f908067.msg.200318.xml.gpg", "2020-03-18"),
    ("f908067.msg.200319.xml.gpg", "2020-03-19"),
    ("f908067.msg.200320.xml.gpg", "2020-03-20"),
    ("f908067.msg.200321.xml.gpg", "2020-03-21"),
    ("f908067.msg.200322.xml.gpg", "2020-03-22"),
    ("f908067.msg.200323.xml.gpg", "2020-03-23"),
    ("f908067.msg.200324.xml.gpg", "2020-03-24"),
    ("f908067.msg.200325.xml.gpg", "2020-03-25"),
    ("f908067.msg.200326.xml.gpg", "2020-03-26"),
    ("f908067.msg.200327.xml.gpg", "2020-03-27"),
    ("f908067.msg.200328.xml.gpg", "2020-03-28"),
    ("f908067.msg.200329.xml.gpg", "2020-03-29"),
    ("f908067.msg.200330.xml.gpg", "2020-03-30"),
    ("f908067.msg.200331.xml.gpg", "2020-03-31"),
]


class TestUtils(unittest.TestCase):
    def test_get_date_from_file_path(self):
        for input, expected in CASES:
            result = utils.get_date_from_file_path(input)
            self.assertEqual(result, expected)
