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

# TODO Zack - What is the "crux" function in this module (file)?

# TODO you can and should re-use this template script often (and maybe refine it)
# TODO for re-use you'd have to, of course, change the "crux" function to what makes sense for your next project/program

import os
import sys
import datetime
from dateutil import parser
from teams import team_abbrevs, team_nicknames
from baseball import show_results

YESTERDAY = str(datetime.datetime.now().date() - datetime.timedelta(days=1))

# default input parameters
defaults = {
    'when':         YESTERDAY,    # only real choices are yesterday or (anything else is today)
    'team':         'CLE',        # the home team
    'alert_runs':   '12',         # int; maybe use as IoT trigger at some point during Summer 2017?
    'from_web':     'True',       # boolean True to scrape from web; otherwise, try to read from local file
}

# we want to remember what defaults were, so let's copy to protect it from changes
parameters = defaults.copy()


def parameters_ok():
    """check for reasonableness of parameters"""

    # TODO what happens if the input argument for team IS in official/known abbrevs?
    # TODO in effect, where does the program flow branch to

    # robustly handle date (day) input string
    try:
        parameters['when'] = parser.parse(parameters['when']).date()
    except Exception, e:
        print 'could not parse "when" =' + parameters['when'] + ' input because ' + e.message
        return False

    # we want from_web to be boolean type (not a string)
    parameters['from_web'] = parameters['from_web'].title() == 'True'

    # FIXME if from_web is False, we naively assume local file exists here, so put explicit check here

    # robustly handle team argument (abbreviation, nickname, upper/lowercase, and such)
    parameters['team'] = parameters['team'].upper()  # make it uppercase for convenience
    if not parameters['team'] in team_abbrevs:
        # if input argument for team NOT in official/known abbrevs, then
        # python will run this indented block of code below the if
        nickname = team_nicknames.get(parameters['team'], None)
        if not nickname:
            print 'cannot work with team = %s' % parameters['team']
            return False
        else:
            parameters['team'] = team_nicknames[parameters['team']]

    # command line args are strings, but we want alert_runs as an int
    try:
        parameters['alert_runs'] = int(parameters['alert_runs'])
    except Exception, e:
        print 'could not convert alert_runs to int > %s' % e.message
        return False

    return True  # all OK; otherwise, return False somewhere above in this def


def print_usage():
    """print helpful text how to run the program"""
    # print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def scrape_web(params):
    """briefly state what your actual work is going to do here"""
    if params['from_web']:
        print 'Scrape MLB web page with these parameters:', params
    else:
        print 'Try to read local file with these parameters:', params
    # print 'These were the defaults                           :', defaults
    date = params['when']
    team = params['team']
    alert_runs = params['alert_runs']
    from_web = params['from_web']
    show_results(date, team, alert_runs=alert_runs, from_web=from_web)


def main(args):
    """describe main routine here"""

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
