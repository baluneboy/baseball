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
from teams import team_abbrevs, team_nicknames
from baseball import show_results


# default input parameters
defaults = {
    'date':         'YESTERDAY',    # string that can be parsed to produce a date object
    'team':         'CLE',        # string abbrev for default (home/my) team; ignored when min_runs > 998
    'min_runs':     '999',        # int minimum number of runs scored by any team -- IoT trigger during Summer 2017?
    'from_web':     'True',       # boolean True to scrape from web; otherwise, read from local file (if exists)
}

_DEFAULT_DATE = datetime.datetime.now().date() - datetime.timedelta(days=1)
_DEFAULT_TEAM = 'CLE'
_DEFAULT_RUNS = 999
_DEFAULT_FROM_WEB = True

def date_parsed_str(s):
    """return datetime date object converted from input string, s"""
    dtm = date_parser.parse(s)
    return dtm.date()


def parse_inputs():
    parser = argparse.ArgumentParser()


    # date of game
    help_date = "date of game; default=%s" % str(_DEFAULT_DATE)
    parser.add_argument('-d', '--date', nargs=1, default=_DEFAULT_DATE,
                        type=date_parsed_str,
                        help=help_date)

    # team of interest
    help_team = 'team of interest; default=%s' % _DEFAULT_TEAM
    parser.add_argument('team', nargs='?', default=_DEFAULT_TEAM,
                        type=str,
                        help=help_team)

    # minimum number of runs scored by a team in a game to trigger runs_callback
    help_runs = "minimum number runs scored by a team in a game to trigger runs_callback; default=%d" % _DEFAULT_RUNS
    parser.add_argument('runs', nargs='?', default=_DEFAULT_RUNS,
                        type=int,
                        help=help_runs)

    # boolean for getting game data source from web, if True; otherwise from local cache if it exists
    help_from_web = "get game data by scraping MLB web page"
    help_not_from_web = "get game data from local cached file (if it exists)"
    #parser.add_argument('from_web', nargs='?', default=_DEFAULT_FROM_WEB,
    #                    type=bool,
    #                    help=help_from_web)
    parser.add_argument('-w', '--from-web',     dest='from_web', action='store_true', help=help_from_web)
    parser.add_argument('-n', '--not-from-web', dest='from_web', action='store_false', help=help_not_from_web)
    parser.set_defaults(from_web=True)

    # verbosity
    parser.add_argument("-v", "--verbosity",
                        action="count",
                        help="increase output verbosity")

    # return parsed args
    return parser.parse_args()


def show_args(args):

    # demo show
    my_date = args.date
    if args.verbosity == 2:
        print "date of game was {}".format(str(args.date))
    elif args.verbosity == 1:
        print "date = {}".format(str(args.date))
    else:
        print my_date
    print args

# we want to remember what defaults were, so let's copy to protect it from changes
parameters = defaults.copy()


def parameters_ok():
    """check for reasonableness of parameters that will be used"""

    # FIXME return False if an input argument does not match defaults keys

    # check for unexpected arguments
    for p in parameters:
        if not p in defaults.keys():
            print 'unexpected input argument name %s' % p
            return False

    # TODO what happens if the input argument for team IS in official/known abbrevs?
    # TODO in effect, where does the program flow branch to

    # robustly handle date (day) input string
    try:
        parameters['date'] = parser.parse(parameters['date']).date()
    except Exception, e:
        print 'could not parse "date" =' + parameters['date'] + ' input because ' + e.message
        return False

    # we want from_web to be boolean type (not a string)
    parameters['from_web'] = parameters['from_web'].title() == 'True'

    # FIXME if from_web is False, we naively assume local file exists here; put explicit check for file here

    # command line arguments come in as strings, but we want min_runs as an int
    try:
        parameters['min_runs'] = int(parameters['min_runs'])  # type cast as int
    except Exception, e:
        # FIXME use None as value to signal downstream call that we want to ignore min_runs
        print 'ignoring min_runs, could not convert to int because %s' % e.message
        print 'FIXME - THIS IS WHERE WE WANT TO USE None FOR DOWNSTREAM FLAG TO IGNORE min_runs'
        return False

    # TODO how can we handle min_runs of zero AND isolate/identify "my team" (input arg) at same time?

    # if min_runs is reasonable value to use, then we need to check all scores (so we can ignore team input argument)
    if parameters['min_runs'] < 999:
        parameters['team'] = ''
    else:
        # robustly handle team argument (abbreviation, nickname, upper/lowercase, and such)
        parameters['team'] = parameters['team'].upper()  # make it uppercase for convenience (as a convention)
        if not parameters['team'] in team_abbrevs:
            # if input argument for team NOT in official/known abbrevs, then
            # python will run this indented block of code below the if
            nickname = team_nicknames.get(parameters['team'], None)
            if not nickname:
                print 'unknown team identifier: %s' % parameters['team']
                return False
            else:
                parameters['team'] = team_nicknames[parameters['team']]

    return True  # all OK; otherwise, return False somewhere above in this def


def print_usage():
    """print helpful text how to run the program"""
    # print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def scrape_web(params):
    """fetch and print results based on input params"""
    if params['from_web']:
        print 'Scrape MLB web page with these parameters:', params
    else:
        print 'Try to read local file with these parameters:', params
    # print 'These were the defaults                           :', defaults
    date = params['date']
    team = params['team']
    min_runs = params['min_runs']
    from_web = params['from_web']
    show_results(date, team, min_runs=min_runs, from_web=from_web)


def main(args):
    """handle input arguments and return Linux-like status code that comes from lower-level function"""

    # parse command line arguments
    for p in args[1:]:
        pair = p.split('=')
        if 2 != len(pair):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            scrape_web(parameters)
            return 0
    print_usage()


if __name__ == '__main__':
    """run main with command line args and return exit code"""
    # sys.exit(main(sys.argv))
    args = parse_inputs()
    show_args(args)
