# sleeper-best-ball
Compute Best Ball scores on your https://sleeper.app/ league

## Usage Support:
```
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
                        Number of Starting Running Backs in your league (Default 2)
  -r NUM_WR, --num_wr NUM_WR
                        Number of Starting Wide Receivers in your league (Default 2)
  -q NUM_QB, --num_qb NUM_QB
                        Number of Starting Quarterbacks in your league (Default 1)
  -t NUM_TE, --num_te NUM_TE
                        Number of Starting Tight Ends in your league (Default 1)
  -f NUM_FLEX, --num_flex NUM_FLEX
                        Number of Starting Flex(WR/RB/TE) in your league (Default 2)
```

## Sample Response:

### Calculate the best ball scores for a 12 team league for 2018
```
$ python fantasy_football.py -i 123456789012345678 -y 2018
Team                Score
Team 1              1251.0
Team 2              1384.8
Team 3              1395.0
Team 4              1430.0
Team 5              1474.2
Team 6              1527.2
Team 7              1540.0
Team 8              1580.1
Team 9              1608.3
Team 10             1629.0
Team 11             1646.0
Team 12             1668.6
```
### Calculate the best ball scores for a 12 team league for 2018's Week 1
```
$ python fantasy_football.py -i 123456789012345678 -y 2018 -w 1
Team                Score
Team 1              93.8
Team 2              98.3
Team 3              100.8
Team 4              103.0
Team 5              109.2
Team 6              109.7
Team 7              118.5
Team 8              121.2
Team 9              122.9
Team 10             123.1
Team 11             137.5
Team 12             144.4
```
