#!/usr/bin/env python

# this code adapted from https://github.com/fspinillo/python-baseball.git
# he had no LICENSE file, so I am adding MIT License to include coverage
# of this module (file)

import sys
from datetime import datetime, timedelta
import requests
import json


def get_game_results(game):
    """return game status when team is not selected (blank)"""
    status = game['status']['status']
    if status == "In Progress":
        return '%s (%s) vs %s (%s) @ %s %s' % (
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                game['venue'],
                game['status']['status']
            )
    elif status == "Final" or status == "Game Over":
        return '%s (%s) vs %s (%s) @ %s %s' % (
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                game['venue'],
                game['status']['status']
            )
    elif status == "Pre-Game" or status == "Preview":
        return '%s vs %s @ %s %s%s %s' % (
                game['away_team_name'],
                game['home_team_name'],
                game['venue'],
                game['home_time'],
                game['hm_lg_ampm'],
                game['status']['status']
            )
    else:
        return 'unhandled game status'


def get_team_results(game):
    """return game status when team has been selected"""
    status = game['status']['status']
    if status == "In Progress":
        return \
        '-------------------------------\n' \
        '%s (%s) vs. %s (%s) @ %s\n' \
        '%s: %s of the %s\n' \
        'Pitching: %s || Batting: %s || S: %s B: %s O: %s\n' \
        '-------------------------------' % (
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
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
        '%s (%s) vs. %s (%s) @ %s\n' \
        'W: %s || L: %s || SV: %s\n' \
        '-------------------------------' % (
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                game['venue'],
                game['winning_pitcher']['name_display_roster'],
                game['losing_pitcher']['name_display_roster'],
                game['save_pitcher']['name_display_roster']
            )
    elif status == "Pre-Game" or status == "Preview":
        return \
        '-------------------------------\n' \
        '%s vs %s @ %s %s%s\n' \
        'P: %s || P: %s\n' \
        '-------------------------------' % (
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


def date_url(d):
    """return URL string for feed to scrape based on input date object, d"""
    url_str = "http://gd2.mlb.com/components/game/mlb/year_%d/month_%02d/day_%02d/master_scoreboard.json" % \
              (d.year, d.month, d.day)
    return url_str


def show_results(day, team, alert_runs=12, from_web=True):
    """describe what this returns and inputs too"""

    # we cache (to debug) in case web site blocks on excessive hits from same ip address
    if from_web:
        # build json data structure from feed
        baseball_data = requests.get(date_url(day))
        game_data = baseball_data.json()
    else:
        # FIXME we naively assume local file exists here
        # read json data from local file
        fname = '/Users/ken/Documents/baseball/' + day.isoformat() + '.json'
        with open(fname, 'r') as data_file:
            game_data = json.load(data_file)

    # get game data as array
    game_array = game_data['data']['games']['game']

    # TODO use alert_runs to trigger something (think IoT)
    print '*** We are currently ignoring alert_runs = %d. ***' % alert_runs

    # FIXME how do we handle double-headers?

    # display results for team of interest
    for game in game_array:
        if team == "":
            results = get_game_results(game)
            if results:
                print results
        else:
            if team in [game['home_name_abbrev'], game['away_name_abbrev']]:
                results = get_team_results(game)
                if results:
                    print results


if __name__ == '__main__':

    # get day of interest
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    date = yesterday

    my_team = "CLE"
    min_runs = 12
    from_web = False
    show_results(date, my_team, alert_runs=min_runs, from_web=from_web)
