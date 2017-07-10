#!/usr/bin/env python

# This file follows a particular pattern that you will get familiar with.  We use this pattern quite a bit to process
# microgravity acceleration data and related info from the International Space Station.

# This module (file) is a template with these notable features:
# - defaults dict near top to handle command line input arguments
# - parameters copy of defaults << this is what we use for program's inputs
# - a boolean parameters_ok function that returns True if parameters are all ok; otherwise return False
# - a print_usage function in case something is not expected during input argument handling
# - some form of "run/process the data" [the "crux"] function, where your actual work happens
# - a main function to get us from raw form of input arguments to something we can deal with to actually run

# TODO Zack - How many functions are in this module (file), and which looks most important and why?

# TODO you can and should re-use this template script often (and maybe refine it) for command line type programs

# TODO ask me how to change this so you can re-use it to do other things

import os
import sys
import datetime
from dateutil import parser
from teams import team_abbrevs, team_nicknames
from baseball import show_results

YESTERDAY = str(datetime.datetime.now().date() - datetime.timedelta(days=1))

# default input parameters
defaults = {
    'date':         YESTERDAY,    # string that can be parsed to produce a date object
    'team':         'CLE',        # string abbrev for default (home/my) team; ignored when min_runs > 998
    'min_runs':     '999',        # int minimum number of runs scored by any team -- IoT trigger during Summer 2017?
    'from_web':     'True',       # boolean True to scrape from web; otherwise, read from local file (if exists)
}

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
    sys.exit(main(sys.argv))
