#!/usr/bin/env python

# this code was adapted from https://github.com/fspinillo/python-baseball.git
# which had no LICENSE file, so I am adding MIT License to include coverage
# of this module (file)...oh, and "baseball has been berry berry good to me"

import sys
import json
import requests

from bbargparse import parse_inputs, show_args, print_usage, get_json_filename


# FIXME gracefully handle when team you wanted did not play on date you wanted

# TODO add date neatly into each game result display

# TODO more thoughtful display format (date from game data, cache-read vs. web-scraped, etc.)


def date_url(d):
    """return URL string for web page to scrape based on input date, d"""
    url_str = "http://gd2.mlb.com/components/game/mlb/year_%d/month_%02d/day_%02d/master_scoreboard.json" % \
              (d.year, d.month, d.day)
    return url_str


# TODO refactor these next 2 def's to handle whether team is blank or not

def get_game_results(game, min_runs=999):
    """return game status when team is not selected (blank)"""
    status = game['status']['status']
    runs_home = game['linescore']['r']['home']
    runs_away = game['linescore']['r']['away']
    if status == "In Progress":
        return '%s (%s) vs %s (%s) @ %s %s' % (
                game['away_team_name'],
                runs_away,
                game['home_team_name'],
                runs_home,
                game['venue'],
                status
            )
    elif status == "Final" or status == "Game Over":
        if int(runs_home) >= min_runs or int(runs_away) >= min_runs:
            alert_prefix = '*** '
        else:
            alert_prefix = ''
        return '%s%s (%s) vs %s (%s) @ %s %s' % (
                alert_prefix,
                game['away_team_name'],
                runs_away,
                game['home_team_name'],
                runs_home,
                game['venue'],
                status
            )
    elif status == "Pre-Game" or status == "Preview":
        return '%s vs %s @ %s %s%s %s' % (
                game['away_team_name'],
                game['home_team_name'],
                game['venue'],
                game['home_time'],
                game['hm_lg_ampm'],
                status
            )
    else:
        return 'unhandled game status'


def get_team_results(game, min_runs=999):
    """return game status when team has been selected"""
    status = game['status']['status']
    runs_home = game['linescore']['r']['home']
    runs_away = game['linescore']['r']['away']
    if int(runs_home) >= min_runs or int(runs_away) >= min_runs:
        alert_prefix = '*** '
    else:
        alert_prefix = ''
    if status == "In Progress":
        return \
        '-------------------------------\n' \
        '%s%s (%s) vs. %s (%s) @ %s\n' \
        '%s: %s of the %s\n' \
        'Pitching: %s || Batting: %s || S: %s B: %s O: %s\n' \
        '-------------------------------' % (
                alert_prefix,
                game['away_team_name'],
                runs_away,
                game['home_team_name'],
                runs_home,
                game['venue'],
                game['status']['status'],
                game['status']['inning_state'],
                game['status']['inning'],
                game['pitcher']['last'],
                game['batter']['last'],
                game['status']['s'],
                game['status']['b'],
                game['status']['o']
            )
    elif status == "Final" or status == "Game Over":
        return \
        '-------------------------------\n' \
        '%s%s (%s) vs. %s (%s) @ %s\n' \
        'W: %s || L: %s || SV: %s\n' \
        '-------------------------------' % (
            alert_prefix,
            game['away_team_name'],
                runs_away,
                game['home_team_name'],
                runs_home,
                game['venue'],
                game['winning_pitcher']['name_display_roster'],
                game['losing_pitcher']['name_display_roster'],
                game['save_pitcher']['name_display_roster']
            )
    elif status == "Pre-Game" or status == "Preview":
        return \
        '-------------------------------\n' \
        '%s%s vs %s @ %s %s%s\n' \
        'P: %s || P: %s\n' \
        '-------------------------------' % (
            alert_prefix,
            game['away_team_name'],
                game['home_team_name'],
                game['venue'],
                game['home_time'],
                game['hm_lg_ampm'],
                game['away_probable_pitcher']['name_display_roster'],
                game['home_probable_pitcher']['name_display_roster']
               )
    else:
        return 'unhandled game status'


def show_results(args):
    """describe what this returns and inputs too"""

    # FIXME refactor this function to get rid of following clunky line
    day, team, min_runs, from_web = args.date, args.team, args.runs, args.from_web

    # we cache (to debug) in case web site blocks on excessive hits from same ip address
    if from_web:
        # build json data structure from feed
        baseball_data = requests.get(date_url(day))
        game_data = baseball_data.json()
    else:
        # FIXME this should be a graceful try/except handler
        # read json data from local file
        json_file = get_json_filename(args)
        with open(json_file, 'r') as data_file:
            game_data = json.load(data_file)

    # get game data as array
    game_array = game_data['data']['games']['game']

    # TODO use alert_runs to trigger something (think IoT usefulness or interesting demo)

    # FIXME how are double-headers handled?

    # display results for team of interest
    for game in game_array:
        if team == "":
            results = get_game_results(game, min_runs=min_runs)
            if results:
                print results
        else:
            if team in [game['home_name_abbrev'], game['away_name_abbrev']]:
                results = get_team_results(game)
                if results:
                    print results


def main(args):
    """handle input arguments and return Linux-like status code that comes from call to get game day results"""

    # FIXME need to verify parameters or otherwise validate input

    # parse command line arguments
    if True:  # parameters_ok():

        if args.from_web:
            print 'Scrape MLB web page with these parameters:'
            show_args(args)
        else:
            print 'Try to read local (cached) file with these parameters:'

        show_results(args)

        return 0

    print_usage()


if __name__ == '__main__':
    """run main with command line args and return exit code"""
    input_args = parse_inputs()
    sys.exit(main(input_args))
