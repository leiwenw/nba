import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_teams():
  url = 'http://espn.go.com/nba/teams'
  r = requests.get(url)

  soup = BeautifulSoup(r.text)
  tables = soup.find_all('ul', class_='medium-logos')

  teams = []
  prefix_1 = []
  prefix_2 = []
  teams_array = []
  for table in tables:
    lis = table.find_all('li')
    for li in lis:
      info = li.h5.a
      teams.append(info.text.encode('ascii'))
      url = info['href']
      prefix_1.append(url.split('/')[-2])
      prefix_2.append(url.split('/')[-1])

  for index, team in enumerate(teams):
    teams_array.append({'name': team, 'prefix_1': prefix_1[index], 'prefix_2': prefix_2[index]})

  dic = {'prefix_2': prefix_2, 'prefix_1': prefix_1}
  teams = pd.DataFrame(dic, index=teams)
  teams.index.name = 'name'


  #print(teams_array)
  return teams_array

