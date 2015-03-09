import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime, date
from datetime import date, timedelta
import simplejson, json

#*******************************************************************
# get_num_games
#*******************************************************************
def get_num_games(team_key1, schedule_dic, adate):
  begin_date = adate
  end_date = adate
  games_this_week = 0
  
  while (begin_date.weekday() != 0):
    begin_date = begin_date - timedelta(days=1)

  while (end_date.weekday() != 6):
    end_date = end_date + timedelta(days=1)

  for game in schedule_dic[team_key1]:
    if (game['date'] >= begin_date and game['date'] <= end_date):
      #print game['date']
      games_this_week += 1


  #print "Begin: " + str(begin_date) + ". End: " + str(end_date)
  #print games_this_week
  return games_this_week


#*******************************************************************
# get_teams
#*******************************************************************
def get_teams(update):
  if (update):
    url = 'http://espn.go.com/nba/teams'
    r = requests.get(url)

    soup = BeautifulSoup(r.text)
    tables = soup.find_all('ul', class_='medium-logos')

    team_names = []
    team_key1 = []
    team_key2 = []
    team_dic = {}
    
    for table in tables:
      lis = table.find_all('li')
      for li in lis:
        info = li.h5.a
        team_names.append(info.text.encode('ascii'))
        url = info['href']
        team_key1.append(url.split('/')[-2].encode('ascii'))
        team_key2.append(url.split('/')[-1].encode('ascii'))

    for index, team in enumerate(team_names):
      team_dic[team_key1[index]] = {'name': team, 'key1': team_key1[index], 'key2': team_key2[index]}

    with open('data/team_data.json', 'w') as outfile:
      json.dump(team_dic, outfile)
  
  else:
    json_data = open('data/team_data.json')
    team_dic = json.load(json_data)

  #print team_dic
  return team_dic

#*******************************************************************
# get_stats
#*******************************************************************
def get_stats(player_id):
  PLAYER_URL = 'http://espn.go.com/nba/player/_/id/{0}'
  r = requests.get(PLAYER_URL.format(player_id))
  soup = BeautifulSoup(r.text)
  player_stat = {}

  #season stats
  table = soup.findAll('table')[3]
  row = table.find_all('tr')[1]
  cells = row.find_all('td')
  #for idx in range(len(cells)):
  #  print str(idx) + " " + cells[idx].string
  #print ""

  stats_season = {};
  stats_season['fg'] = float(cells[4].string)
  stats_season['ft'] = float(cells[8].string)
  stats_season['ptm3'] = float(re.search(r'(.*)-', cells[5].string).group(1))
  stats_season['pts'] = float(cells[15].string)
  stats_season['reb'] = float(cells[9].string)
  stats_season['ast'] = float(cells[10].string)
  stats_season['st'] = float(cells[12].string)
  stats_season['blk'] = float(cells[11].string)
  stats_season['to'] = float(cells[14].string)

  #last5 stats
  table = soup.findAll('table')[4]
  row = table.find_all('tr')[6]
  cells = row.find_all('td')
  #for idx in range(len(cells)):
  #  print str(idx) + " " + cells[idx].string
  #print ""

  stats_last5 = {};
  stats_last5['fg'] = float(cells[4-1].string)
  stats_last5['ft'] = float(cells[8-1].string)
  stats_last5['ptm3'] = float(re.search(r'(.*)-', cells[5-1].string).group(1))
  stats_last5['pts'] = float(cells[15-1].string)
  stats_last5['reb'] = float(cells[9-1].string)
  stats_last5['ast'] = float(cells[10-1].string)
  stats_last5['st'] = float(cells[12-1].string)
  stats_last5['blk'] = float(cells[11-1].string)
  stats_last5['to'] = float(cells[14-1].string)

  #team info
  team_ul = soup.find_all('ul', class_='general-info')[0]
  team_li = team_ul.find_all('li')[2]

  team_url = team_li.a['href']
  team_str = team_li.text
  team_key1 = team_url.split('/')[-2].encode('ascii')
  team_key2 = team_url.split('/')[-1].encode('ascii')

  #name
  name = soup.find_all('h1')[1].string
  
  player_stat = {'team':team_key1, 'name':name, 'stats_season':stats_season, 'stats_last5':stats_last5}
  
  #print  team_str + team_url + team_key1 + team_key2
  #for key in stats_season:
  #  print key + " " + str(stats_season[key])
  #print stats_season
  #print ""
  #for key in stats_last5:
  #  print key + " " + str(stats_last5[key])
  #print stats_last5

  return player_stat;

#*******************************************************************
# get_schedules
#*******************************************************************
def get_schedules(team_dic, my_year, update):
  schedule_dic = {}
  if update:
    #my_year = 2015
    begin_months = ['Oct','Nov','Dec']
    BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/{2}'
    BASE_GAME_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

    for key, team in team_dic.items():
      team_name = team['name']
      print(team_name)
      r = requests.get(BASE_URL.format(team['key1'], my_year, team['key2']))
      table = BeautifulSoup(r.text).table
      schedule_dic[key] = []

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
          #print dateobj.strftime("%b %d, %Y") + " " + opponent + " " + str(home)

          schedule_dic[key].append({'date':dateobj.strftime("%b %d %Y"), 'opp':opponent, 'home':home})

    with open('data/schedule_data.json', 'w') as outfile:
      json.dump(schedule_dic, outfile)
  
  else:
    json_data = open('data/schedule_data.json')
    schedule_dic = json.load(json_data)
  
  #convert date str to date obj
  for key in schedule_dic:
    for game in schedule_dic[key]:
      game['date'] = datetime.strptime(str(game['date']), '%b %d %Y').date()
  
  return schedule_dic
  #print schedule_dic['sa'][0]
  #print schedule_dic['sa'][0]['opp']
  #games = pd.DataFrame(dic).drop_duplicates(cols='id').set_index('id')
  #print(games)

