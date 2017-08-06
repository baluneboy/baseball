#!/usr/bin/env python

"""This module utilizes urllib from the standard library to fetch json file from MLB web site."""

import os
import sys
import json
import requests
import datetime

import bbargparse as bba

_WEB_RESP_MIN_SIZE = 10000  # bytes (or is this characters -- same difference?)


def content_okay(gdata):
    """return True if crude checks on content of web response (json data) for game day data seems okay"""
    if gdata is None:
        print 'game data (content) is None'
        return False

    if len(gdata) != 3:
        print 'content expected to have len 3 (not len = {1})'.format(len(gdata))
        return False

    # num_games = len(c['data']['games'])
    # print 'num_games', num_games
    # if num_games < 2:
    #     print 'did not expect less than 2 games'
    #     return False

    return True


def date_url(d):
    """return URL string for web page to scrape based on input date, d"""
    url_str = "http://gd2.mlb.com/components/game/mlb/year_%d/month_%02d/day_%02d/master_scoreboard.json" % \
              (d.year, d.month, d.day)
    return url_str


def read_game_data_from_json_file(json_file):
    """read json data from local file"""
    game_data = None
    print 'reading game data from file...',
    try:
        with open(json_file, 'r') as f:
            game_data = json.load(f)
    except IOError as e:
        print "an I/O error({0}): {1} for {2}".format(e.errno, e.strerror, json_file)
    except ValueError:
        print "could not load json game data that was read from json file {0}".format(json_file)
    except:
        print "unhandled exception:", sys.exc_info()[0]
        raise
    else:
        print 'done reading from "{0}"'.format(json_file)
    finally:
        print 'no cleanup needed after reading json file'

    return game_data


def download_json(day, out_dir):
    """download_json json file and return game data; cache file locally if more than one day old"""
    game_data = None
    url_str = date_url(day)
    destination_filename = bba.get_json_filename(out_dir, day)

    # logic to get game_data
    if not os.path.exists(out_dir):
        print 'non-existent output (cache) directory "%s"' % out_dir
    else:
        if os.path.exists(destination_filename):
            print 'using cached json file "%s"' % destination_filename
            game_data = read_game_data_from_json_file(destination_filename)
        else:
            try:
                print 'downloading json file for %s...' % day.isoformat()
                resp = requests.get(url_str)
                # check if day is at least one day (86400 seconds) ago for caching
                dtmoi = datetime.datetime.combine(day, datetime.datetime.max.time())
                delta_secs = (datetime.datetime.now() - dtmoi).total_seconds()
                # print "delta seconds", delta_secs
                if delta_secs > 86400:
                    print 'saving file to local cache directory'
                    with open(destination_filename, 'w') as f:
                        f.write(resp.content)
                game_data = resp.json()
            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                print 'Timeout issue'
            except requests.exceptions.TooManyRedirects:
                # Tell the user their URL was bad and try a different one
                print 'TooManyRedirects issue'
            except requests.exceptions.RequestException as e:
                # catastrophic error
                print e
            print 'done with download_json'

    if not content_okay(game_data):
        print 'game data (json) content does not seem okay'
        return None

    return game_data


def demo():
    import datetime
    bln = download_json(datetime.date(1981, 7, 6), '/Users/ken/Documents/baseball')
    print bln


if __name__ == '__main__':
    demo()
