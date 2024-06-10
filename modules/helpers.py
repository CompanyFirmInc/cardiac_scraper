import os
import datetime

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')  # Format the date