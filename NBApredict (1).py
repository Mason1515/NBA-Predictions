#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import statistics
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashteamstats, teamdashboardbygeneralsplits, scoreboard, leaguegamefinder




# Set up team id numbers in dictionaries and initialize the targetted statistical categories

all_teams = teams.get_teams()
team_list = list(team['full_name'] for team in all_teams)

global stats
stats = ['TOV','PTS', 'REB','W_PCT','PLUS_MINUS','FG_PCT']

id_by_team = {}
for team in all_teams:
    if team['full_name'] in team_list:
        id_by_team[team['full_name']] = team['id']
        
teams_by_id = dict((val,key) for key,val in id_by_team.items())



# Uncomment if you want to look at the league team dashboard

#league_dash = leaguedashteamstats.LeagueDashTeamStats().get_data_frames()[0]
#league_dash



# This function gets the team stats for a given team

def get_stats(team):
    team_stats = {}
    team_dash = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(id_by_team[team]).get_data_frames()[0]
    for stat in stats:
         team_stats[stat] = team_dash[stat][0]
            
    return team_stats
    
# Get the league average of the particular stat
    
def get_average(stat):
    return statistics.mean(list(i for i in league_dash[stat]))
    


# Initialize the dictionary containing all the teams stats to quickly access the data for the actual predictive calculations

stats_by_team = {}
for team in team_list:
    stats_by_team[team] = get_stats(team)



# Find the standard deviation of the numbers in the data set of each stat

def deviation(stat):
    stat_all = []
    for i in league_dash[stat]:
        stat_all.append(i)
        
    return statistics.stdev(stat_all)

# Find z score for each stat for a team

def zScore(stat,mean,stdev):
    return (stat-mean) / stdev

# Use those z scores in comparison to the other team in the matchup and find their z score differentials

def zScoreDiffs(home,away):
    zDiffs = {}
    
    for stat in stats:
        home_score = zScore(stats_by_team[home][stat],get_average(stat),deviation(stat))
        away_score = zScore(stats_by_team[away][stat],get_average(stat),deviation(stat))
        
        zDiffs[stat] = home_score - away_score
        
    return zDiffs


# When going through each z score differential, adjust the win chance percentage

def predict(home,away):
        
    home_WP = .55
    
    diffs = zScoreDiffs(home,away)
    
    for stat in diffs:
        if stat == 'TOV':
            if diffs[stat] > 0 and diffs[stat] < 1:
                home_WP -= .033
            elif diffs[stat] > 1:
                home_WP -= .066
            if diffs[stat] < 0 and diffs[stat] > -1:
                home_WP += .033
            elif diffs[stat] < -1:
                home_WP += .066
        else:
            if diffs[stat] > 1:
                home_WP += .066
            elif diffs[stat] < -1:
                home_WP -= .066
            elif diffs[stat] > -1 and diffs[stat] < -.25:
                home_WP -= .033
            elif diffs[stat] < 1 and diffs[stat] > 0.25:
                home_WP += .033
            elif diffs[stat] < 0 and diffs[stat] > -.25:
                home_WP -= 0
            else:
                home_WP += 0
                
    home_WP = round(home_WP,2)
                
    print(f"{home_WP * 100}% chance the {home} will beat the {away}")

    
# Look up matchups that are scheduled today and return a dictionary    
    
def getMatchups():
    
    matchups = scoreboard.Scoreboard().get_data_frames()[0]
    all_matchups = {}
    for i in matchups['GAME_SEQUENCE']:
        all_matchups[i] = []
    
    home_teams = list(i for i in matchups['HOME_TEAM_ID'])
    away_teams = list(i for i in matchups['VISITOR_TEAM_ID'])
    
    for key,val in enumerate(home_teams):
        if key + 1 in all_matchups:
            all_matchups[key + 1].append(teams_by_id[val])
            
    for key,val in enumerate(away_teams):
        if key + 1 in all_matchups:
            all_matchups[key + 1].append(teams_by_id[val])
    
        
    return all_matchups


# Use the getMatchups functions and then loop through the dictionary predicting all the scheduled matchups

def predictAllMatchups():
    all_matchups = getMatchups()
    
    for game in all_matchups:
        predict(all_matchups[game][0],all_matchups[game][1])
        
# Find all scheduled matchups on a specific date in the future 

def getGamesOnDate(date):
    
    games = scoreboard.Scoreboard(game_date=date).get_data_frames()[0]
    all_matchups = {}
    for i in games['GAME_SEQUENCE']:
        all_matchups[i] = []
    
    home_teams = list(i for i in games['HOME_TEAM_ID'])
    away_teams = list(i for i in games['VISITOR_TEAM_ID'])
    
    for key,val in enumerate(home_teams):
        if key + 1 in all_matchups:
            all_matchups[key + 1].append(teams_by_id[val])
            
    for key,val in enumerate(away_teams):
        if key + 1 in all_matchups:
            all_matchups[key + 1].append(teams_by_id[val])
    
        
    return all_matchups

# Predict all matchups on that future date 

def predictGamesOnDate(date):
    all_games = getGamesOnDate(date)
    
    for game in all_games:
        predict(all_games[game][0],all_games[game][1])



#predictAllMatchups()





