# sleeper-best-ball
Compute Best Ball scores on your https://sleeper.app/ league

## Usage Support:
```
$ python calculate_best_ball_scores.py -h
usage: calculate_best_ball_scores.py [-h] -i LEAGUE_ID -y YEAR [-w WEEK]
                                     [-b NUM_RB] [-r NUM_WR] [-q NUM_QB]
                                     [-t NUM_TE] [-f NUM_FLEX [-s SORT_BY]

Get Sleeper App Best Ball Scores

optional arguments:
  -h, --help            show this help message and exit
  -i LEAGUE_ID, --league_id LEAGUE_ID
                        The ID of your Sleeper League
  -y YEAR, --year YEAR  Which year to work with (i.e. 2018).
  -w WEEK, --week WEEK  Which week to work with (i.e. 1), for full season
                        leave blank
  -e END_WEEK, --end_week END_WEEK
                        Sum of all weeks till the end week. Default to 13 for
                        13 week season.
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
  -s SORT_BY, --sort_by SORT_BY
                        Sort by "score" or "record". (Default Score)
```

## Sample Response:

### Calculate the best ball scores for a 12 team league for 2018
```
$ python calculate_best_ball_scores.py -i 123456789012345678 -y 2018
Team                Score               Record(W-L-T)
Team 1              1251.0              0-12-0
Team 2              1384.8              0-12-0
Team 3              1395.0              0-12-0
Team 4              1430.0              6-6-0
Team 5              1474.2              6-6-0
Team 6              1527.2              6-6-0
Team 7              1540.0              6-6-0
Team 8              1580.1              6-6-0
Team 9              1608.3              6-6-0
Team 10             1629.0              12-0-0
Team 11             1646.0              12-0-0
Team 12             1668.6              12-0-0
```
### Calculate the best ball scores for a 12 team league for 2018's Week 1
```
$ python calculate_best_ball_scores.py -i 123456789012345678 -y 2018 -w 1
Team                Score               Record(W-L-T)
Team 1              93.8                0-1-0
Team 2              98.3                0-1-0
Team 3              100.8               0-1-0
Team 4              103.0               0-1-0
Team 5              109.2               0-1-0
Team 6              109.7               0-1-0
Team 7              118.5               1-0-0
Team 8              121.2               1-0-0
Team 9              122.9               1-0-0
Team 10             123.1               1-0-0
Team 11             137.5               1-0-0
Team 12             144.4               1-0-0
```
### Calculate the best ball scores for a 12 team league for 2019 from Week 1 to 3
```
$ python calculate_best_ball_scores.py -i 123456789012345678 -y 2019 -e 3
Team                Score               Record(W-L-T)
Team 1              198.3               0-3-0
Team 2              215.2               0-3-0
Team 3              220.1               0-3-0
Team 4              224.5               1-2-0
Team 5              247.8               1-2-0
Team 6              248.1               1-2-0
Team 7              249.4               2-1-0
Team 8              255.2               2-1-0
Team 9              263.1               2-1-0
Team 10             272.5               3-0-0
Team 11             281.1               3-0-0
Team 12             285.9               3-0-0
```
### Calculate the best ball records for a 12 team league for 2019 from Week 1 to 8
```
$ python calculate_best_ball_scores.py  -i 123456789012345678 -y 2019 -e 8 -s record
Team                Record(W-L-T)       Score
Team 1              1-7-0               893.9
Team 2              2-6-0               883.5
Team 3              2-6-0               784.0
Team 4              3-5-0               771.3
Team 5              4-4-0               1003.1
Team 6              4-4-0               887.9
Team 7              4-4-0               1111.1
Team 8              5-3-0               966.3
Team 9              5-3-0               950.8
Team 10             5-3-0               938.6
Team 11             6-2-0               1108.3
Team 12             7-1-0               1000.5
```
