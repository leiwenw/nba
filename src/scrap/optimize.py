#!/usr/bin/python
import espn
import itertools
from datetime import datetime, date
from scipy.stats import norm

stat_categories = ['fg', 'ft', 'ptm3', 'pts', 'reb', 'ast', 'st', 'blk', 'to']
score_mode = ['stats_season', 'stats_last5']
my_team = [3975, 2394, 4249, 215, 3015, 4257, 2758, 609, 1015]
my_potentials =[]

def main():
  my_team_stats = {} #dict with all players and their season, last5, and total stats
  set_max = {} #dict of the max stats
  all_sets_stat = [] #list of all possible combos, and their respective stats

  regenerate = 0
  active_players = 6

  print "Optimize"
  
  team_dic = espn.get_teams(regenerate)
  schedule_dic = espn.get_schedules(team_dic, 2015, regenerate)
  #adate = date(2015, 3, 10)
  adate = datetime.today().date()
  
  for player_id in my_team:
    player_stats = espn.get_stats(player_id)
    num_games = espn.get_num_games(player_stats['team'], schedule_dic, adate)

    stats_week = {}
    for mode in score_mode:
      stats_week[mode] = {}
      for cate in stat_categories:
        if (cate == 'fg' or cate == 'ft'):
          stats_week[mode][cate] = player_stats[mode][cate]
        else:
          stats_week[mode][cate] = player_stats[mode][cate] * num_games

    player_stats['stats_week'] = stats_week
    player_stats['num_games'] = num_games
    my_team_stats[player_id] = player_stats
  #print my_team_stats

  all_sets = find_combos(my_team, active_players)
  print all_sets

  #calculate combo scores
  for aset in all_sets:
    set_stat = {}
    set_stat['set'] = aset
    for mode in score_mode:
      set_stat[mode] = {}
      for cate in stat_categories:
        set_stat[mode][cate] = 0
        for player_id in aset:
          if (cate == 'fg' or cate == 'ft'):
            set_stat[mode][cate] += my_team_stats[player_id]['stats_week'][mode][cate]/active_players
          else:
            set_stat[mode][cate] += my_team_stats[player_id]['stats_week'][mode][cate]

    all_sets_stat.append(dict(set_stat))
  
  #figure out max stats for each category
  for mode in score_mode:
    set_max[mode] = {}

  for set_stat in all_sets_stat:
    for player_id in set_stat['set']:
      print my_team_stats[player_id]['name'] + " " + str(my_team_stats[player_id]['stats_week']['stats_season']['ft']) + " " + str(my_team_stats[player_id]['stats_week']['stats_season']['pts'])
    print set_stat

    for mode in score_mode:
      for cate in stat_categories:
        if cate not in set_max[mode]:
          set_max[mode][cate] = float(set_stat[mode][cate])
        elif cate == 'to' and set_stat[mode][cate] < set_max[mode][cate]:
          set_max[mode][cate] = float(set_stat[mode][cate])
        elif cate != 'to' and set_stat[mode][cate] > set_max[mode][cate]:
          set_max[mode][cate] = float(set_stat[mode][cate])
    set_stat['score'] = 0

  #print all_sets_stat
  norm.cdf(1.96)
  print set_max
  #print_excel(all_sets_stat)

def print_excel(all_sets_stat):
  for mode in score_mode:
    print "*********************************************************************************\n\n"
    for set_stat in all_sets_stat:
      for cate in stat_categories:
        print(str(set_stat[mode][cate]) + "\t"),
      print ""
    print "*********************************************************************************\n\n"

def find_combos(my_team, active_players):
  #my_team = [0,1,2,3,4,5,6,7,8] #for testing
  all_sets = list(itertools.combinations(my_team, active_players))
  return all_sets

def find_combos_dumb(my_team, active_players):
  #find all combos
  all_sets = []
  for a in range(0,4):
    working_set = []
    working_set.append(my_team[a])
    for b in range(a+1,5):
      working_set.append(my_team[b])
      for c in range(b+1,6):
        working_set.append(my_team[c])
        for d in range(c+1,7):
          working_set.append(my_team[d])
          for e in range(d+1,8):
            working_set.append(my_team[e])
            for f in range(e+1,9):
              working_set.append(my_team[f])
              #print working_set
              all_sets.append(list(working_set))
              working_set.pop()
            working_set.pop()
          working_set.pop()
        working_set.pop()
      working_set.pop()
    working_set.pop()
  return all_sets

if __name__ == "__main__":
  main()
