#!/usr/bin/env python

"""This module utilizes urllib from the standard library to fetch json file from MLB web site."""

import os
import requests
from baseball import date_url
from bbargparse import get_json_filename


def download_json(day, out_dir):
    """try to download file, then return True if successfully saved in out_dir using day in filename"""
    url_str = date_url(day)
    destination_filename = get_json_filename(out_dir, day)
    if os.path.exists(destination_filename):
        print 'no need to download json because "%s" exists already' % destination_filename
        return False

    try:
        print 'downloading json file for %s...' % day.isoformat()
        resp = requests.get(url_str)
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print 'Timeout issue'
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        print 'TooManyRedirects issue'
    except requests.exceptions.RequestException as e:
        # catastrophic error
        print e
        return False

    print 'done with download'

    with open(destination_filename, 'w') as f:
        f.write(resp.content)

    return True


def demo():
    import datetime
    bln = download_json(datetime.date(1901, 7, 5), '/Users/ken/Documents/baseball')
    print bln


if __name__ == '__main__':
    demo()
