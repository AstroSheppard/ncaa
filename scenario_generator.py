import numpy as np
import pandas as pd
import random
import sys
import matplotlib.pyplot as plt

# Function to put winners into dataframe
def get_winners(teams, winners):
    index=list(teams.index)
    lose=[]
    for i in range(0,len(teams),2):
        if winners.iloc[i,0] == 1:
            lose.append(index[i+1])
        else:
            lose.append(index[i])
     
    teams=teams.drop(lose)
    
    return teams

def generator(survivors, brackets, winners, nRounds):
    # nRounds are the amount of rounds remaining. 4 for sweet 16, 3 for elite 8, etc.
 
    # Simulate winners of each round for 1 run
    sim=pd.DataFrame()
    for i in range(nRounds):
        survivors=get_winners(survivors, winners)
        sim=sim.append(survivors)
        start=2**(nRounds-i)
        winners=winners[start:]
 
    sim_winners=sim['matchups']
    print sim_winners
    # Append winners to bracket pool array
    nPlayers=len(brackets)/63
    for i in range(nPlayers):
        brackets.iloc[63*i:63*(i+1),4][-2**nRounds+1:]=sim_winners

    brackets['Correct?']=(brackets['Picks'] == brackets['Winner'])
    brackets['Points']=brackets['Round']*brackets['Correct?']

    results=pd.DataFrame()
    ptest=[]
    rtest=[]
    for i in range(nPlayers): 
        ptest.append(brackets.iloc[63*i,1])
        rtest.append(brackets.iloc[63*i:63*(i+1),-2].sum())
        brackets.iloc[63*i:63*(i+1),-1]=brackets.iloc[63*i:63*(i+1),-2].sum()
    results['Player']=ptest
    results['Points']=rtest
    return results.sort_values(by='Points', ascending=False)   

###############################################################################

if __name__ == "__main__":

    # Read in brackets 
    winners=pd.read_csv('scenario.csv')
    brackets=pd.read_csv('./espn/bracket_data.csv')

    #payouts=[160, 90, 60, 30]   

    # Determine the amount of teams left
    nTeams=int(winners['nLeft'][0])
    nRounds=int(np.log(nTeams)/np.log(2))

    # Make dataframe containing only remaining teams
    survivors=pd.DataFrame()
    survivors['matchups']=brackets['Winner'][64-2*nTeams:64-nTeams]

    # Define empty dataframe 
    results=pd.DataFrame()
    nPlayers=len(brackets['Bracket Name'].drop_duplicates())
    rank=range(1,nPlayers+1)

    # Determine rankings given scenario
    results=generator(survivors, brackets, winners, nRounds)
    results['Rank']=rank
 
    print(results)
