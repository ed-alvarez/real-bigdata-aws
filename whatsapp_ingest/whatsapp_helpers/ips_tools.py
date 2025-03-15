"""
Handy common tools
"""
import logging
import math

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
