#!/usr/bin/env python

"""This module utilizes argparse from the standard library to define what arguments it requires, and figure out how to
parse those from sys.argv.  The argparse module automatically generates help and usage messages and issues errors when
users give the program invalid arguments.
"""

import os
import argparse
import datetime
from dateutil import parser as date_parser

from teams import team_abbrevs


_DEFAULT_DATE = datetime.datetime.now().date() - datetime.timedelta(days=1)
_DEFAULT_TEAM = 'CLE'
_DEFAULT_RUNS = 999
_DEFAULT_FROM_WEB = True
_DEFAULT_CACHE = '/Users/ken/Documents/baseball'


def date_str(d):
    """return datetime date object converted from input string, s"""
    dtm = date_parser.parse(d)
    return dtm.date()


def runs_str(r):
    """return valid min_runs int value converted from string, r"""
    try:
        value = int(r)
    except Exception, e:
        raise argparse.ArgumentTypeError('minimum runs could not be converted from %s' % e.message)

    if value < 1 or value > 999:
        raise argparse.ArgumentTypeError('minimum runs has to be 1 <= r <= 999')

    return value


def team_str(t):
    """return string provided as uppercase if it exists in team_abbrevs"""
    t = t.upper()
    if t not in team_abbrevs:
        raise argparse.ArgumentTypeError('"%s" is not in official list of team_abbrevs' % t)
    return t


def cache_str(c):
    """return string provided if dir exists locally"""
    if not os.path.exists(c):
        raise argparse.ArgumentTypeError('"%s" does not exist as local cache dir' % c)
    return c


def get_json_filename(loc_dir, day):
    """return string for full filename of local cached json file given local directory, loc_dir, and date of interest"""
    return os.path.join(loc_dir, day.isoformat() + '.json')


def parse_inputs():
    """parse input arguments using argparse from standard library"""
    parser = argparse.ArgumentParser(description='"Baseball has been berry, berry good to me."')

    # date of game
    help_date = "date of game; default=%s" % str(_DEFAULT_DATE)
    parser.add_argument('-d', '--date', default=_DEFAULT_DATE,
                        type=date_str,
                        help=help_date)

    # team of interest
    help_team = 'team of interest; default=%s' % _DEFAULT_TEAM
    parser.add_argument('-t', '--team', default=_DEFAULT_TEAM,
                        type=team_str,
                        help=help_team)

    # local cache directory
    help_cache = 'cache directory; default=%s' % _DEFAULT_CACHE
    parser.add_argument('-c', '--cache', default=_DEFAULT_CACHE,
                        type=cache_str,
                        help=help_cache)

    # minimum number of runs scored by a team in a game to trigger runs_callback
    help_runs = "minimum number runs scored by a team in a game to trigger runs_callback; default=%d" % _DEFAULT_RUNS
    parser.add_argument('-r', '--runs', default=_DEFAULT_RUNS,
                        type=runs_str,
                        help=help_runs)

    # boolean for getting game data source from web, if True; otherwise from local cache if it exists
    help_not_from_web = "get game data from local cached file (if it exists)"
    parser.add_argument('-n', '--not-from-web', dest='from_web', default=True,
                        action='store_false',
                        help=help_not_from_web)
    parser.set_defaults(from_web=True)

    # verbosity
    parser.add_argument("-v", "--verbosity",
                        action="count",
                        help="increase output verbosity")

    # get parsed args
    args = parser.parse_args()

    # FIXME where is pythonic spot for checking parsed args
    # if not web-scraping, then check for locally cached json file
    if not args.from_web:
        json_file = get_json_filename(args.cache, args.date)
        if not os.path.exists(json_file):
            raise Exception('"%s" does not exist as local json file' % json_file)

    return args


def show_args(args):
    """print arguments"""

    # demo show
    my_date = args.date
    if args.verbosity == 2:
        print "date of game is {}".format(str(args.date))
    elif args.verbosity == 1:
        print "date = {}".format(str(args.date))
    else:
        print my_date
    print args


def print_usage():
    """print helpful text how to run the program"""
    # print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


