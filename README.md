# sleeper-best-ball
Compute Best Ball scores on your https://sleeper.app/ league

$ python calculate_best_ball_scores.py -h
usage: calculate_best_ball_scores.py [-h] -i LEAGUE_ID -y YEAR [-w WEEK]
                                     [-b NUM_RB] [-r NUM_WR] [-q NUM_QB]
                                     [-t NUM_TE] [-f NUM_FLEX]

Get Sleeper App Best Ball Scores

optional arguments:
  -h, --help            show this help message and exit
  -i LEAGUE_ID, --league_id LEAGUE_ID
                        The ID of your Sleeper League
  -y YEAR, --year YEAR  Which year to work with (i.e. 2018).
  -w WEEK, --week WEEK  Which week to work with (i.e. 1), for full season
                        leave blank
  -b NUM_RB, --num_rb NUM_RB
                        Number of Starting Running Backs in your league
  -r NUM_WR, --num_wr NUM_WR
                        Number of Starting Wide Receivers in your league
  -q NUM_QB, --num_qb NUM_QB
                        Number of Starting Quarterbacks in your league
  -t NUM_TE, --num_te NUM_TE
                        Number of Starting Tight Ends in your league
  -f NUM_FLEX, --num_flex NUM_FLEX
                        Number of Starting Flex(WR/RB/TE) in your league
