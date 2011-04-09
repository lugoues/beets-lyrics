import sys

def scrub(str):
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    try:
        return str.encode(encoding)
    except UnicodeError:
        return str.encode('utf-8')

