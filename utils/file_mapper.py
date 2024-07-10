import re


def file_mapper(filename):
    retname = re.sub(r'[^a-zA-Z0-9_]', '', filename)
    return retname[:10]
