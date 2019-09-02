from enum import Enum
import requests
import argparse

def get_user_id_to_team_name(league_id):
    user_id_to_team_name = {}
    r = requests.get("https://api.sleeper.app/v1/league/%s/users" % league_id)
    user_data = r.json()
    for user in user_data:
        user_id_to_team_name[user['user_id']] = user['display_name']
    return user_id_to_team_name

def get_roster_id_to_owner(user_id_to_team_name, league_id):
    roster_id_to_owner = {}
    r = requests.get('https://api.sleeper.app/v1/league/%s/rosters' % league_id)
    roster_info = r.json()
    for roster in roster_info:
        name = user_id_to_team_name[roster['owner_id']]
        roster_id_to_owner[roster['roster_id']] = name
    return roster_id_to_owner

def get_owner_to_roster(roster_id_to_owner, league_id, week):
    owner_to_roster = {}
    r = requests.get('https://api.sleeper.app/v1/league/%s/matchups/%s' %
        (league_id, week))
    rosters = r.json()
    for roster in rosters:
        owner = roster_id_to_owner[roster['roster_id']]
        owner_to_roster[owner] = roster['players']
    return owner_to_roster

def get_player_id_to_info():
    player_id_to_info = {}
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    players = r.json()
    for player_id in players:
        player = players[player_id]
        if player['fantasy_positions']:
            position = player['fantasy_positions'][0]
            if position in ('RB', 'WR', 'QB', 'TE'):
                player_id_to_info[player_id] = (
                    player['search_full_name'], position)
            else:
                continue
    return player_id_to_info

def get_player_to_points(year, week, player_id_to_info):
    player_id_to_points = {}
    r = requests.get('https://api.sleeper.app/v1/stats/nfl/regular/%s/%s' %
        (year, week))
    players = r.json()
    for player_id in players:
        if ('pts_half_ppr' in players[player_id]
            and player_id in player_id_to_info):
            player_id_to_points[player_id] = (
                players[player_id]['pts_half_ppr'], player_id_to_info[player_id]
                )
        else:
            continue
    return player_id_to_points

def get_points(rbs, wrs, qbs, tes, roster_count):
    flex = rbs[roster_count['rb']:] + \
           wrs[roster_count['wr']:] + \
           tes[roster_count['te']:]
    flex.sort(reverse=True)
    return sum(rbs[:roster_count['rb']]) + \
           sum(wrs[:roster_count['wr']]) + \
           sum(qbs[:roster_count['qb']]) + \
           sum(tes[:roster_count['te']]) + \
           sum(flex[:roster_count['flex']])

def get_owner_to_score(
    owner_to_roster, player_to_points, player_id_to_info, roster_count):
    owner_to_score = {}
    for owner in owner_to_roster:
        rbs = []
        wrs = []
        qbs = []
        tes = []
        for player in owner_to_roster[owner]:
            if player in player_to_points:
                points, (fullname, position) = player_to_points[player]
                if position == 'RB':
                    rbs.append(points)
                elif position == 'WR':
                    wrs.append(points)
                elif position == 'QB':
                    qbs.append(points)
                elif position == 'TE':
                    tes.append(points)
                else:
                    continue
            else:
                continue
        rbs.sort(reverse=True)
        wrs.sort(reverse=True)
        qbs.sort(reverse=True)
        tes.sort(reverse=True)
        owner_to_score[owner] = get_points(rbs, wrs, qbs, tes, roster_count)
    return owner_to_score

def parse_args():
    parser = argparse.ArgumentParser(
        description='Get Sleeper App Best Ball Scores')
    parser.add_argument(
        '-i', '--league_id', help='The ID of your Sleeper League', required=True
        )
    parser.add_argument(
        '-y','--year', help='Which year to work with (i.e. 2018).',
        required=True)
    parser.add_argument(
        '-w', '--week', 
        help='Which week to work with (i.e. 1), for full season leave blank',
        required=False)
    parser.add_argument(
        '-b', '--num_rb',
        help='Number of Starting Running Backs in your league (Default 2)', 
        required=False, default=2, type=int)
    parser.add_argument(
        '-r', '--num_wr',
        help='Number of Starting Wide Receivers in your league (Default 2)',
        required=False, default=2, type=int)
    parser.add_argument(
        '-q', '--num_qb', 
        help='Number of Starting Quarterbacks in your league (Default 1)',
        required=False, default=1, type=int)
    parser.add_argument(
        '-t', '--num_te', 
        help='Number of Starting Tight Ends in your league (Default 1)',
        required=False, default=1, type=int)
    parser.add_argument(
        '-f', '--num_flex',
        help='Number of Starting Flex(WR/RB/TE) in your league (Default 2)', 
        required=False, default=2, type=int)
    return vars(parser.parse_args())

if __name__ == "__main__":
    args = parse_args()
    league_id = args['league_id']
    year = args['year']
    week = args['week']
    roster_count = {}
    roster_count['rb'] = args['num_rb']
    roster_count['wr'] = args['num_wr']
    roster_count['qb'] = args['num_qb']
    roster_count['te'] = args['num_te']
    roster_count['flex'] = args['num_flex']

    user_id_to_team_name = get_user_id_to_team_name(league_id)
    roster_id_to_owner = get_roster_id_to_owner(user_id_to_team_name, league_id)
    player_id_to_info = get_player_id_to_info()
    final_owner_to_score = {}
    if week:
        player_to_points = get_player_to_points(year, week, player_id_to_info)
        owner_to_roster = get_owner_to_roster(roster_id_to_owner, league_id, week)
        final_owner_to_score = get_owner_to_score(
            owner_to_roster, player_to_points, player_id_to_info, roster_count)
    else:
        # We only care about up to week 13 since thats the end of the fantasy
        # regular season.
        for week in range(1,14):
            owner_to_roster = get_owner_to_roster(
                roster_id_to_owner, league_id, week)
            player_to_points = get_player_to_points(
                year, week, player_id_to_info)
            owner_to_score = get_owner_to_score(
                owner_to_roster, player_to_points, player_id_to_info, 
                roster_count)
            for owner in owner_to_score:
                if owner in final_owner_to_score:
                    final_owner_to_score[owner] += owner_to_score[owner]
                else:
                    final_owner_to_score[owner] = owner_to_score[owner]
    
    sorted_scores = final_owner_to_score.items()
    sorted_scores.sort(key=lambda tup: tup[1]) # sort by the scores
    sorted_scores.insert(0, ('Team', 'Score'))
    for score in sorted_scores:
        print("{0:<20}{1:<20}".format(score[0], score[1]))
