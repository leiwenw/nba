#!/usr/bin/python
import espn
from datetime import datetime, date

def main():
  stat_categories = ['fg', 'ft', 'ptm3', 'pts', 'reb', 'ast', 'st', 'blk', 'to']
  my_team = [3975, 2394, 4249, 215, 3015, 4257, 2758, 609, 1015]
  my_team_stats = {}
  my_potentials =[]
  regenerate = 0
  season_or_last = 'stats_last5' #options are stats_season or stats_last5
  season_or_last = 'stats_season' #options are stats_season or stats_last5
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
    for cate in stat_categories:
      if (cate == 'fg' or cate == 'ft'):
        stats_week[cate] = player_stats[season_or_last][cate]
      else:
        stats_week[cate] = player_stats[season_or_last][cate] * num_games

    player_stats['stats_week'] = stats_week
    player_stats['num_games'] = num_games
    my_team_stats[player_id] = player_stats
  print my_team_stats

  #find all combos
  #my_team = [0,1,2,3,4,5,6,7,8]
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
  #print all_sets

  #calculate combo scores
  all_sets_stat = []
  for aset in all_sets:
    set_stat = {}
    set_stat['set'] = aset
    for cate in stat_categories:
      set_stat[cate] = 0
    for player_id in aset:
      for cate in stat_categories:
        if (cate == 'fg' or cate == 'ft'):
          set_stat[cate] += my_team_stats[player_id]['stats_week'][cate]/active_players
        else:
          set_stat[cate] += my_team_stats[player_id]['stats_week'][cate]

    all_sets_stat.append(dict(set_stat))
  
  set_max = {}
  #for cate in stat_categories:
  #  set_max[cate] = 0

  for set_stat in all_sets_stat:
    for player_id in set_stat['set']:
      print my_team_stats[player_id]['name'] + " " + str(my_team_stats[player_id]['stats_week']['ft']) + " " + str(my_team_stats[player_id]['stats_week']['pts'])
    print set_stat

    for cate in stat_categories:
      if cate not in set_max:
        set_max[cate] = set_stat[cate]
      elif cate == 'to' and set_stat[cate] < set_max[cate]:
        set_max[cate] = set_stat[cate]
      elif set_stat[cate] > set_max[cate]:
        set_max[cate] = set_stat[cate]


    set_stat['score'] = 0

  #print all_sets_stat
  print set_max

if __name__ == "__main__":
  main()
