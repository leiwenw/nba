#!/usr/bin/python

import re
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

my_year = 2015
teams = [
    {'name': 'Boston Celtics', 'prefix_1': 'bos', 'prefix_2': 'boston-celtics'},
    {'name': 'San Antonio Spurs', 'prefix_1': 'sa', 'prefix_2': 'san-antonio-spurs'},
    ]
begin_months = ['Oct','Nov','Dec']
BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/{2}'
BASE_GAME_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

print teams
game_id = []
dates = []
home_team = []
home_team_score = []
visit_team = []
visit_team_score = []
for team in teams:
  team_name = team['name']
  print(team_name) + "<br>"
  r = requests.get(BASE_URL.format(team['prefix_1'], my_year, team['prefix_2']))
  table = BeautifulSoup(r.text).table
  
  for row in table.find_all('tr')[1:]:
    column = row.find_all('td')
    date = str(column[0])
    
    date_match = re.search(r'\w+,\s(\w+)\s(\d+)', date)
    if date_match:
      month = date_match.group(1)
      day = date_match.group(2)
      if month in begin_months:
        year = my_year - 1
      else:
        year = my_year
      opponent = str(column[1])
      
      home_match = re.search(r'\"game-status\">(vs|\@)<\/li>', opponent)
      if home_match:
        home = home_match.group(1)
        if home == 'vs':
          home = True
        else:
          home = False

      opp_match = re.search(re.escape('http://espn.go.com/nba/team/_/name/') + '(\w+)\/',opponent)
      if opp_match:
        opponent = opp_match.group(1)
      
      date = month + " " + day + " " + str(year)
      dateobj = datetime.strptime(date, '%b %d %Y')
      print dateobj.strftime("%b %d, %Y") + " " + opponent + " " + str(home)

dic = {'id': game_id, 'date': dates, 'home_team': home_team, 'visit_team': visit_team, 
    'home_team_score': home_team_score, 'visit_team_score': visit_team_score}
#games = pd.DataFrame(dic).drop_duplicates(cols='id').set_index('id')
#print(games)
