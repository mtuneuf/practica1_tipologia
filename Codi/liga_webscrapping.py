#!/usr/bin/env python
# coding: utf-8

# In[81]:


import os
import requests
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://playerstats.football/la-liga'

validCompetitions = ["La Liga", "Copa del Rey", "Champions League", "Europa League"]


def getValue(value):
    if(isinstance(value,list)):
        value = value[0]
    
    number = [float(s) for s in re.findall(r'-?\d+\.?\d*', value)][0]
    
    return number

def checkCompetition(comp):
    
    if(comp in validCompetitions):
        return True
    
    return False

def getTeams():    
    req = requests.get(url)

    soup = BeautifulSoup(req.text, "html.parser")

    teams = soup.find_all('tr')

    teamsUrl = []

    for team in teams:
        teamUrl = team.find('a')['href']
        teamsUrl.append(teamUrl)
    
    return teamsUrl

def getTeamStatistics(teamUrl):
    splittedUrl = teamUrl.split("/")
    team = "/"+splittedUrl[len(splittedUrl) - 1]
    
    fullUrl = url + team
    
    reqTeam = requests.get(fullUrl)
    
    soup = BeautifulSoup(reqTeam.text, "html.parser")
    
    table = soup.find_all("div", {"class":'stat-ctn'})[0]
    
    rows = table.find_all("div", {"class": "stat player-stat-row"})
    
    statDict = {}
    
    competitionsTag = soup.find_all("div", {"class": "stat__fixture stat__fixture--image"})
    
    competitions = []
    
    for comp in competitionsTag:
        
        competition = comp.find("img").get("title")
    
        competitions.append(competition)
    
    for row in rows:
        statName = row.find("div", {"class": "stat__player"}).contents[0]
        statName = statName.replace('\n', '')
        
        
        if(statName == "Throw-ins"):
            break;

        totalStat = 0
        countStat = 0
        
        statNumbers = row.find_all("div", {"class": "stat__fixture player-stat-no"})
        
        i = 0
        for stat in statNumbers:
            
            if(checkCompetition(competitions[i]) == False):
                break;
                
            if len(stat) == 1:
                number = stat.contents
            else:
                sibling = stat.find_all("span", {"class": "smallno"})[0].find_previous_siblings("div")
                if len(sibling) > 0:
                    number = sibling[0].contents
                else:
                    number = stat.contents[0]
            number = getValue(number)
            
            totalStat += number
            countStat += 1
        
            i += 1
        
        if(countStat != 0):
            statDict.update({statName: totalStat/countStat})
    
    return statDict, splittedUrl[len(splittedUrl) - 1]
   
        

teams = getTeams()

df = pd.DataFrame()

for team in teams:  
    teamDict, teamName = getTeamStatistics(team)
    teamDict.update({'Name': teamName})
    series = pd.Series(teamDict)
    df = df.append(series, ignore_index=True)

columnList = df.columns.to_list()
columnList[0], columnList[2] = columnList[2], columnList[0]

df = df[columnList]

df.to_csv(path_or_buf='laligaStats.csv', index=False)


# DOI: 10.5281/zenodo.5636156

# In[ ]:




