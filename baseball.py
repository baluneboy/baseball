#!/usr/bin/env python

# this code was adapted from https://github.com/fspinillo/python-baseball.git
# which had no LICENSE file, so I am adding MIT License to include coverage
# of this module (file)...oh, and "baseball has been berry berry good to me"

import os
import sys

import bbargparse
import download_json

# FIXME when a rainout (postpone) occurs do we get linescore error and how to gracefully handle

# FIXME only cache file if date of interest was 1 day ago or earlier

# FIXME gracefully handle when team you wanted did not play on date you wanted

# TODO how to get ALL via what mechanism [ team = 'all' ? ]

# TODO introduce config file/parser for things (like at least) good default cache dir setting

# TODO add date neatly into each game result display

# TODO more thoughtful display format (date from game data, cache-read vs. web-scraped, etc.)

# TODO refactor these next 2 def's to handle whether team is blank or not


def get_game_results(game, min_runs=999):
    """return game status when team is not selected (blank)"""
    status = game['status']['status']
    if status.lower() == 'postponed':
        # FIXME add a few more details (like teams, field)
        return 'postponed'
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
    if status.lower() == 'postponed':
        # FIXME add a few more details (like teams, field)
        return 'postponed'
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


def divide(x, y):
    result = None
    try:
        result = x / y
    except ZeroDivisionError:
        print "division by zero!"
    except:
        print "unhandled exception:", sys.exc_info()[0]
        raise
    else:
        print "done with result", result
    finally:
        print "executing finally clause"

    return result


def show_results(args):
    """show game results based on input args for date and team of interest"""

    # we cache local files: MLB should not rewrite history OR in case their site blocks on excessive hits from my ip
    if args.from_web:
        # build json data structure from feed
        # ### baseball_data = requests.get(date_url(day))
        # ### game_data = baseball_data.json()
        game_data = download_json.download_json(args.date, args.cache)
        if game_data is None:
            print 'something went wrong with download_json'
            return False

    # FIXME this should be a graceful try/except handler, we naively assume all's well with now getting from cached file
    else:
        # read game data from json file
        json_file = bbargparse.get_json_filename(args.cache, args.date)
        game_data = download_json.read_game_data_from_json_file(json_file)

    # get game data as array
    game_array = game_data['data']['games']['game']

    # TODO use alert_runs to trigger something (think IoT usefulness or interesting demo)

    # FIXME how are double-headers handled?

    # display results for team of interest
    for game in game_array:
        if args.team == "":
            results = get_game_results(game, min_runs=args.runs)
            if results:
                print results
        else:
            if args.team in [game['home_name_abbrev'], game['away_name_abbrev']]:
                results = get_team_results(game)
                if results:
                    print results

    return True


def args_ok(a):
    """return boolean True if args ok; otherwise squawk and return False"""
    # FIXME where is pythonic spot for checking parsed args
    bln = True
    # if not from web, then only check for locally cached json file
    if not a.from_web:
        json_file = bbargparse.get_json_filename(a.cache, a.date)
        if not os.path.exists(json_file):
            print 'you chose not-from-web option, but "%s" does not exist' % json_file
            bln = False
    return bln


def main():
    """handle input arguments and return Linux-like status code that comes from call to show game day results"""

    # FIXME need to verify parameters or otherwise validate input

    # parse command line arguments
    args = bbargparse.parse_inputs()

    # if args not ok, then squawk and return exit code of -1
    if not args_ok(args):
        return -1

    # show desired game day results
    show_results(args)

    # return exit code zero for success
    return 0


if __name__ == '__main__':
    """run main with command line args and return exit code"""
    sys.exit(main())
