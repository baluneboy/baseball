#!/usr/bin/env python

"""This module utilizes argparse from the standard library to define what arguments it requires, and figure out how to
parse those from sys.argv.  The argparse module automatically generates help and usage messages and issues errors when
users give the program invalid arguments.
"""

import os
import sys
import argparse
import datetime
from dateutil import parser as date_parser
from teams import team_abbrevs
from baseball import show_results


_DEFAULT_DATE = datetime.datetime.now().date() - datetime.timedelta(days=1)
_DEFAULT_TEAM = 'CLE'
_DEFAULT_RUNS = 999
_DEFAULT_FROM_WEB = True


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
    if not t in team_abbrevs:
        raise argparse.ArgumentTypeError('"%s" is not in official list of team_abbrevs' % t)
    return t


def parse_inputs():
    """parse input arguments using argparse from standard library"""
    parser = argparse.ArgumentParser()

    # date of game
    help_date = "date of game; default=%s" % str(_DEFAULT_DATE)
    parser.add_argument('-d', '--date', nargs=1, default=_DEFAULT_DATE,
                        type=date_str,
                        help=help_date)

    # team of interest
    help_team = 'team of interest; default=%s' % _DEFAULT_TEAM
    parser.add_argument('-t', '--team', default=_DEFAULT_TEAM,
                        type=team_str,
                        help=help_team)

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

    # return parsed args
    return parser.parse_args()


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


def get_bbgame_results(args):
    """fetch and print results based on input arguments"""
    if args.from_web:
        print 'Scrape MLB web page with these parameters:'
        show_args(args)
    else:
        print 'Try to read local file with these parameters:'
        show_args(args)
    #show_results(args.date, args.team, min_runs=args.runs, from_web=args.from_web)


def main(args):
    """handle input arguments and return Linux-like status code that comes from lower-level function"""

    # parse command line arguments
    # FIXME need to verify parameters or otherwise validate input
    if True:  # parameters_ok():
        get_bbgame_results(args)
        return 0
    print_usage()


if __name__ == '__main__':
    """run main with command line args and return exit code"""
    args = parse_inputs()
    sys.exit(main(args))
