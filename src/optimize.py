#!/usr/bin/python
import espn
import itertools
import numpy
from datetime import datetime, date, timedelta
from scipy.stats import norm
import operator
import sys

stat_categories = ['fg', 'ft', 'ptm3', 'pts', 'reb', 'ast', 'st', 'blk', 'to']
score_mode = ['stats_season', 'stats_last5']
my_team = [3975, 2394, 4249, 215, 3015, 4257, 2758, 609, 1015]
#my_team = [3975, 2394, 4249, 215, 3015, 4257, 2758, 609, 1015, 6433, 6466, 3244]
my_potentials =[6433, 6466, 3244]
top_num = 10
active_players = 6
chars_break = 100

def main():
  my_team_stats = {} #dict with all players and their season, last5, and total stats

  regenerate = 0

  print "Optimize\n"
  
  team_dic = espn.get_teams(regenerate)
  schedule_dic = espn.get_schedules(team_dic, 2015, regenerate)
  
  for player_id in my_team:
    player_stats = espn.get_stats(player_id)
    my_team_stats[player_id] = player_stats
  
  #adate = date(2015, 3, 10)
  adate = datetime.today().date() + timedelta(days=0)
  print_header("This Week. " + espn.get_week(adate))
  print_stats_week(my_team_stats, schedule_dic, adate)
  adate = datetime.today().date() + timedelta(days=7)
  print_header("Next Week. " + espn.get_week(adate))
  print_stats_week(my_team_stats, schedule_dic, adate)

def print_header(header):
  print_chars('*', chars_break+10)
  print "* " + header
  print_chars('*', chars_break+10)
  print ""

def print_chars(char, n = chars_break):
  for i in range(0, n):
    sys.stdout.write(char)
  print ""

def print_stats_week(my_team_stats, schedule_dic, adate):
  all_sets_stat = [] #list of all possible combos, and their respective stats
  cum_stats = {} #dict of the max stats

  for player_id in my_team:
    num_games = espn.get_num_games(my_team_stats[player_id]['team'], schedule_dic, adate)
    
    stats_week = {}
    for mode in score_mode:
      stats_week[mode] = {}
      for cate in stat_categories:
        if (cate == 'fg' or cate == 'ft'):
          stats_week[mode][cate] = my_team_stats[player_id][mode][cate]
        else:
          stats_week[mode][cate] = my_team_stats[player_id][mode][cate] * num_games
  
    my_team_stats[player_id]['num_games'] = num_games
    my_team_stats[player_id]['stats_week'] = stats_week
  
  all_sets = find_combos(my_team, active_players)

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
  set_max = {}
  for mode in score_mode:
    set_max[mode] = {}

  for set_stat in all_sets_stat:
    for mode in score_mode:
      for cate in stat_categories:
        if cate not in set_max[mode]:
          set_max[mode][cate] = float(set_stat[mode][cate])
        elif cate == 'to' and set_stat[mode][cate] < set_max[mode][cate]:
          set_max[mode][cate] = float(set_stat[mode][cate])
        elif cate != 'to' and set_stat[mode][cate] > set_max[mode][cate]:
          set_max[mode][cate] = float(set_stat[mode][cate])
  
  cum_stats['max'] = set_max
  
  #mean and stddev
  set_mean = {}
  set_stddev = {}
  stat_arr = {}

  for mode in score_mode:
    set_mean[mode] = {}
    set_stddev[mode] = {}
    stat_arr[mode] = {}

  for mode in score_mode:
    for cate in stat_categories:
      stat_arr[mode][cate] = []
      for set_stat in all_sets_stat:
        stat_arr[mode][cate].append(set_stat[mode][cate])
      #print mean_arr[mode]
      #print mode + " " + cate + " " + str(numpy.mean(stat_arr[mode][cate])) + " " + str(numpy.std(stat_arr[mode][cate], ddof=0)) + " " + str(numpy.std(stat_arr[mode][cate], ddof=1))
      set_mean[mode][cate] = numpy.mean(stat_arr[mode][cate])
      set_stddev[mode][cate] = numpy.std(stat_arr[mode][cate], ddof=1)
  
  cum_stats['mean'] = set_mean
  cum_stats['stddev'] = set_stddev
  
  #calculate score
  for set_stat in all_sets_stat:
    set_scores = {}
    set_stat['score'] = {}
    for mode in score_mode:
      set_scores[mode] = {}
      temp_scores = []
      for cate in stat_categories:
        if (cate == 'to'):
          set_scores[mode][cate] = norm.cdf(-(set_stat[mode][cate] - cum_stats['mean'][mode][cate])/cum_stats['stddev'][mode][cate])
          temp_scores.append(set_scores[mode][cate])
        else:
          set_scores[mode][cate] = norm.cdf((set_stat[mode][cate] - cum_stats['mean'][mode][cate])/cum_stats['stddev'][mode][cate])
          temp_scores.append(set_scores[mode][cate])
      set_stat['score'][mode] = float(numpy.mean(temp_scores)*100)
    set_stat['scores'] = dict(set_scores)
  norm.cdf(1.96)
  
  #print all_sets_stat
  sorted(all_sets_stat, key=lambda set_stat: set_stat['score']['stats_last5'])
  
  top_players = {}
  for player_id in my_team:
    top_players[player_id] = 0
  
  for mode in score_mode:
    rank = 1
    print "* Top " + str(top_num) + " combo: " + mode + " optimized:\n"
    for set_stat in sorted(all_sets_stat, key=lambda set_stat: set_stat['score'][mode],reverse=True)[:top_num]:
      print "%-20s %7s" % ("", "Games"),
      for cate in stat_categories:
        print "%7s" % (cate),
      print ""
      print_chars('-')
      print "\n" + "#" + str(rank)
      rank += 1
      total_games = 0
      for player_id in set_stat['set']:
        total_games += my_team_stats[player_id]['num_games']
        print "%-20s %7d" % (my_team_stats[player_id]['name'], my_team_stats[player_id]['num_games']),
        for cate in stat_categories:
          print "%7.2f" %(my_team_stats[player_id]['stats_week']['stats_season'][cate]),
        print ""
        top_players[player_id] += 1

      print ""
      print "%-20s %7d" % ("TOTAL", total_games),
      for cate in stat_categories:
        print "%7.2f" %(set_stat[mode][cate]),
      print ""
      print "%-20s %7s" % ("NORMALIZED", ""),
      for cate in stat_categories:
        print "%7.2f" %(set_stat['scores'][mode][cate]*100),
      print "%7.2f" % (set_stat['score'][mode])
      print ""
    print_chars("*", chars_break + 10)
    print ""
    #print "*********************************************************************************\n"
  
  print "Top Player Counts:\n"
  for player_id in sorted(top_players.items(), key=operator.itemgetter(1), reverse=True):
    #print my_team_stats[player_id[0]]['name'] + "\t\t" + str(my_team_stats[player_id[0]]['num_games']) + "\t" + str(player_id[1])
    print "%-20s %7d %7d" % (my_team_stats[player_id[0]]['name'], my_team_stats[player_id[0]]['num_games'], player_id[1])
  print ""

  #print cum_stats
  #print_excel(all_sets_stat)

def print_excel(all_sets_stat):
  for mode in score_mode:
    print "*********************************************************************************\n"
    for set_stat in all_sets_stat:
      for cate in stat_categories:
        print(str(set_stat[mode][cate]) + "\t"),
      print ""
    print "*********************************************************************************\n"

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
