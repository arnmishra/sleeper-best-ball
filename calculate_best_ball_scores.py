from enum import Enum
import requests
import argparse
import nflgame

def get_user_id_to_team_name(league_id):
    """
    Gets a map of fantasy player user id to their team name
    """
    user_id_to_team_name = {}
    r = requests.get("https://api.sleeper.app/v1/league/%s/users" % league_id)
    user_data = r.json()
    for user in user_data:
        user_id_to_team_name[user['user_id']] = user['display_name']
    return user_id_to_team_name

def get_roster_id_to_owner(user_id_to_team_name, league_id):
    """
    Gets a map of the roster id to the fantasy owner team name
    """
    roster_id_to_owner = {}
    r = requests.get('https://api.sleeper.app/v1/league/%s/rosters' % league_id)
    roster_info = r.json()
    for roster in roster_info:
        name = user_id_to_team_name[roster['owner_id']]
        roster_id_to_owner[roster['roster_id']] = name
    return roster_id_to_owner

def get_owner_to_roster(player_id_to_custom_id, roster_id_to_owner, league_id, week):
    """
    Gets a map of the owner team name to the roster players
    Also determines which two teams are in each matchup by getting a map of
    matchu pid to the two owners playing the game
    """
    owner_to_roster = {}
    matchup_id_to_owners = {}
    r = requests.get('https://api.sleeper.app/v1/league/%s/matchups/%s' %
        (league_id, week))
    rosters = r.json()
    for roster in rosters:
        owner = roster_id_to_owner[roster['roster_id']]
        player_ids = roster['players']
        custom_ids = [player_id_to_custom_id[player_id] for player_id in player_ids]
        owner_to_roster[owner] = custom_ids
        matchup_id = roster['matchup_id']
        if matchup_id in matchup_id_to_owners:
            matchup_id_to_owners[matchup_id].append(owner)
        else:
            matchup_id_to_owners[matchup_id] = [owner]
    return owner_to_roster, matchup_id_to_owners

def get_player_id(first_name, last_name, team):
    """
    Returns a custom player ID of first initial + last name + team
    i.e. for Tom Brady in New England that is T.Brady-NE
    """
    if (team == None):
        team = 'None'
    return first_name[0] + "." + last_name + "-" + team

def get_custom_id_to_info():
    """
    Gets a map of player name/team to position
    """
    custom_id_to_info = {}
    player_id_to_custom_id = {}
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    players = r.json()
    for player_id in players:
        player = players[player_id]
        if player['fantasy_positions']:
            position = player['fantasy_positions'][0]
            if position in ('RB', 'WR', 'QB', 'TE'):
                custom_id = get_player_id(player['first_name'], player['last_name'], player['team'])
                if not custom_id:
                    continue
                player_id_to_custom_id[player_id] = custom_id
                custom_id_to_info[custom_id] = position
    return custom_id_to_info, player_id_to_custom_id

def calculate_player_points(player):
    rushing_score = player.rushing_yds * 0.1 + player.rushing_tds * 6 + player.rushing_twoptm * 2
    passing_score = player.passing_yds * 0.04 + player.passing_tds * 4 + player.passing_twoptm * 2
    receiving_score = player.receiving_yds * 0.1 + player.receiving_tds * 6 + player.receiving_rec * 0.5 + player.receiving_twoptm * 2
    negative_scores = player.passing_ints * 2 + player.fumbles_lost * 2
    return rushing_score + passing_score + receiving_score - negative_scores

def get_player_to_points(year, week, custom_id_to_info):
    """
    Gets a map of player ID to a tuple of the player's points and position
    """
    player_id_to_points = {}
    games = nflgame.games(int(year), week=int(week))
    players = nflgame.combine_game_stats(games)
    for player in players:
        custom_id = player.name + "-" + player.team
        if (custom_id in custom_id_to_info):
            points = calculate_player_points(player)
            player_id_to_points[custom_id] = (points, custom_id_to_info[custom_id])
    print (player_id_to_points)
    return player_id_to_points

def get_points(rbs, wrs, qbs, tes, roster_count):
    """
    Gets the number of points a set of players makes up given the roster counts
    """
    flex = rbs[roster_count['rb']:] + \
           wrs[roster_count['wr']:] + \
           tes[roster_count['te']:]
    flex.sort(reverse=True)
    return sum(rbs[:roster_count['rb']]) + \
           sum(wrs[:roster_count['wr']]) + \
           sum(qbs[:roster_count['qb']]) + \
           sum(tes[:roster_count['te']]) + \
           sum(flex[:roster_count['flex']])

def get_owner_to_score(owner_to_roster, player_to_points, roster_count):
    """
    Gets a map of the owner to their fantasy score
    """
    owner_to_score = {}
    for owner in owner_to_roster:
        rbs = []
        wrs = []
        qbs = []
        tes = []
        for player in owner_to_roster[owner]:
            if player in player_to_points:
                points, position = player_to_points[player]
                if position == 'RB':
                    rbs.append(points)
                elif position == 'WR':
                    wrs.append(points)
                elif position == 'QB':
                    qbs.append(points)
                elif position == 'TE':
                    tes.append(points)
        rbs.sort(reverse=True)
        wrs.sort(reverse=True)
        qbs.sort(reverse=True)
        tes.sort(reverse=True)
        owner_to_score[owner] = get_points(rbs, wrs, qbs, tes, roster_count)
    return owner_to_score

def get_owner_to_weekly_record(matchup_id_to_owners, final_owner_to_score):
    """
    Gets a map of the owner to their best ball record
    """
    owner_to_record = {}
    for matchup_id in matchup_id_to_owners:
        owner_1 = matchup_id_to_owners[matchup_id][0]
        owner_2 = matchup_id_to_owners[matchup_id][1]
        score_1 = final_owner_to_score[owner_1]
        score_2 = final_owner_to_score[owner_2]
        if score_1 > score_2:
            owner_to_record[owner_1] = [1, 0, 0]
            owner_to_record[owner_2] = [0, 1, 0]
        elif score_1 == score_2:
            owner_to_record[owner_1] = [0, 0, 1]
            owner_to_record[owner_2] = [0, 0, 1]
        else:
            owner_to_record[owner_1] = [0, 1, 0]
            owner_to_record[owner_2] = [1, 0, 0]
    return owner_to_record

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
        '-e', '--end_week',
        help='Sum of all weeks till the end week. Default to 13 for 13 week season.',
        required=False, default=13, type=int)
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
    parser.add_argument(
        '-s', '--sort_by',
        help='Sort by score, record, rank, top6. (Default Score)',
        required=False, default='score', type=str)
    return vars(parser.parse_args())

if __name__ == "__main__":
    "Parses all the arguments into variables"
    args = parse_args()
    league_id = args['league_id']
    year = args['year']
    week = args['week']
    end_week = args['end_week']
    roster_count = {}
    roster_count['rb'] = args['num_rb']
    roster_count['wr'] = args['num_wr']
    roster_count['qb'] = args['num_qb']
    roster_count['te'] = args['num_te']
    roster_count['flex'] = args['num_flex']

    # Gets a map of the user id to the owner team name
    user_id_to_team_name = get_user_id_to_team_name(league_id)
    # Gets a map of the roster id to the owner team name
    roster_id_to_owner = get_roster_id_to_owner(user_id_to_team_name, league_id)
    # Gets a map of each player id to their name and position
    custom_id_to_info, player_id_to_custom_id = get_custom_id_to_info()
    # A map to track the owner name to its best ball score
    final_owner_to_score = {}
    # A map of each owner to their best ball record
    final_owner_to_record = {}
    # A map of each owner to their best ball rank
    final_owner_to_rank = {}
    # A map of each owner to number of top 6 best ball performances
    final_owner_to_top_half_or_bottom = {}
    num_teams = len(user_id_to_team_name)
    if week:
        # If we are getting it for an individual week, calculate that data
        # Get the number of fantasy points each player scored that week
        player_to_points = get_player_to_points(year, week, custom_id_to_info)
        # Gets the map of each owner to their players and which two teams are playing each other
        owner_to_roster, matchup_id_to_owners = get_owner_to_roster(
            player_id_to_custom_id, roster_id_to_owner, league_id, week)
        # Gets the best ball score for each owner
        final_owner_to_score = get_owner_to_score(owner_to_roster, player_to_points, roster_count)
        # Gets the best ball record for each owner
        final_owner_to_record = get_owner_to_weekly_record(
            matchup_id_to_owners, final_owner_to_score)
        # Sorts the teams by score and determines if they are top 6
        sorted_by_score = sorted(final_owner_to_score.items(), key=lambda kv: kv[1])
        for i in range(len(sorted_by_score)):
                owner = sorted_by_score[i][0]
                final_owner_to_rank[owner] = [num_teams-i]
                if(i >= 6):
                    final_owner_to_top_half_or_bottom[owner] = 1
    else:
        # If we are getting it for the whole season, calculate that data for each week
        for week in range(1, end_week + 1):
            # Get the number of fantasy points each player scored that week
            player_to_points = get_player_to_points(year, week, custom_id_to_info)
            # Gets the map of each owner to their players and which two teams are playing each other
            owner_to_roster, matchup_id_to_owners = get_owner_to_roster(
                player_id_to_custom_id, roster_id_to_owner, league_id, week)
            # Gets the best ball score for each owner
            owner_to_score = get_owner_to_score(owner_to_roster, player_to_points, roster_count)
            # Gets the best ball record for each owner
            owner_to_record = get_owner_to_weekly_record(
                matchup_id_to_owners, owner_to_score)
            # Adds the total scores and records for each team
            for owner in owner_to_score:
                if owner in final_owner_to_score:
                    final_owner_to_score[owner] += owner_to_score[owner]
                    records = final_owner_to_record[owner]
                    new_record = owner_to_record[owner]
                    final_owner_to_record[owner] = [sum(x) for x in zip(records, new_record)]
                else:
                    final_owner_to_score[owner] = owner_to_score[owner]
                    final_owner_to_record[owner] = owner_to_record[owner]
            # Creates list of tuple of (owner, score) sorted by score
            sorted_by_score = sorted(final_owner_to_score.items(), key=lambda kv: kv[1])
            # Sorts the teams by score and determines if they are top 6
            for i in range(num_teams):
                owner = sorted_by_score[i][0]
                if owner in final_owner_to_rank:
                    final_owner_to_rank[owner].append(num_teams-i)
                else:
                    final_owner_to_rank[owner] = [num_teams-i]
                if(i >= 6):
                    if owner in final_owner_to_top_half_or_bottom:
                        final_owner_to_top_half_or_bottom[owner] += 1
                    else:
                        final_owner_to_top_half_or_bottom[owner] = 1

    # Prints out all the information sorted as the user wants
    for owner in final_owner_to_record:
        final_owner_to_record[owner] = ("-").join([str(elem) for elem in final_owner_to_record[owner]])
        final_owner_to_rank[owner] = round(float(sum(final_owner_to_rank[owner])) / len(final_owner_to_rank[owner]), 2)
        if owner not in final_owner_to_top_half_or_bottom:
            final_owner_to_top_half_or_bottom[owner] = 0
    if args['sort_by'] == 'record':
        sorted_records = final_owner_to_record.items()
        sorted_records = sorted(sorted_records, key=lambda tup: int(tup[1].split("-")[0])) # sort by the records
        print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format('Team', 'Record(W-L-T)', 'Score', 'Top 6 Performances', 'Average Rank'))
        for record in sorted_records:
            owner = record[0]
            print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format(owner, record[1], final_owner_to_score[owner], final_owner_to_top_half_or_bottom[owner], final_owner_to_rank[owner]))
    elif args['sort_by'] == 'rank':
        sorted_rank = final_owner_to_rank.items()
        sorted_rank = sorted(sorted_rank, key=lambda tup: tup[1], reverse=True) # sort by the ranks
        print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format('Team', 'Average Rank', 'Score', 'Record(W-L-T)', 'Top 6 Performances'))
        for rank in sorted_rank:
            owner = rank[0]
            print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format(owner, rank[1], final_owner_to_score[owner], final_owner_to_record[owner], final_owner_to_top_half_or_bottom[owner]))
    elif args['sort_by'] == 'top6':
        sorted_top6 = final_owner_to_top_half_or_bottom.items()
        sorted_top6 = sorted(sorted_top6, key=lambda tup: tup[1]) # sort by the top 6 performances
        print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format('Team', 'Top 6 Performances', 'Score', 'Record(W-L-T)', 'Average Rank'))
        for top6 in sorted_top6:
            owner = top6[0]
            print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format(owner, top6[1], final_owner_to_score[owner], final_owner_to_record[owner], final_owner_to_rank[owner]))
    elif args['sort_by'] == 'score':
        sorted_scores = final_owner_to_score.items()
        sorted_scores = sorted(sorted_scores, key=lambda tup: tup[1]) # sort by the scores
        print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format('Team', 'Score', 'Record(W-L-T)', 'Top 6 Performances', 'Average Rank'))
        for score in sorted_scores:
            owner = score[0]
            print("{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}".format(owner, score[1], final_owner_to_record[owner], final_owner_to_top_half_or_bottom[owner], final_owner_to_rank[owner]))
    else:
        print("Please enter either 'score', 'record', 'rank', or 'top6' for the sort option. %s isn't recognized" % args['sort_by'])
