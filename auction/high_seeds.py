import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
from openpyxl import load_workbook
import sys

def permute(lose, win, num, ties):
    
    pwin=win # probability of each team winning the exact amount of games
    plose=lose # prob of loss before the game 

    # Make permutator
    # Declare 0s array with length = number of teams (3 or 5, always)
    # Set a 1 for each tie
    base=np.zeros(num)
    for i in range(ties):
        base[i]=1
    sum=0
    # Find all unique combos for each 1 and 0, effectively finding each combo in "num choose ties"
    combos=set(it.permutations(base,num))
    # For each combo, convert to an array. Create an invert array of losses.
    # Switches are set such that for every combo, multiply p(win) for each winning team and p(loss) for each losing to get prob of that exact combo. 
    # Add up all combos to get total probability of x amount of ties for the given number of teams for a given round
    for i in combos:
        win=np.array(i)
        lose=1-win
        sum=sum+np.prod(win*pwin+lose*plose)
    
    return sum

def get_prob(df9):


    #  df9['only_odds'] = df9['rd2_win']
    #  df9['tie1_odds'] = df9['rd2_win']
    #  df9['tie2_odds'] = df9['rd2_win']
    #  df9['tie3_odds'] = df9['rd2_win']
    j=0
    for team in df9['team_name']:

        #Isolate current team
        current=df9[df9['team_name'] == team]
 
        #Find all teams with seeds worse than this ones
        seed=current['team_seed'].values[0]
        lower=df9[df9['team_seed'] > seed]
    
        # And note all better seeds
        higher=df9[df9['team_seed'] < seed]

        # And same seed

        same=df9[(df9['team_seed'] == seed) & (df9['team_name'] != team)]
     
  
        same_probs=same.loc[:,'rd2_win':'rd6_win'].values-same.loc[:,'rd3_win':'rd7_win'].values
        #Array containg, for each team, exact prob of finishing in each spot. To get prob of not reaching round: 1-np.sum(same_probs[i,j:])
 
        
        #Declare prob arrays
        probs=np.zeros(5)
        lprobs=np.zeros(5)
        hprobs=np.zeros(5)
        # Arrays for same seed factor. Separate depending on amount of teams that tie
        tie1=np.zeros(5)
        tie2=np.zeros(5)
        tie3=np.zeros(5)
        only=np.zeros(5)
        prob=0
        probt1=0
        probt2=0
        probt3=0

        # Probability for every other team to not advance to a given round
        lloss=1-lower.loc[:,'rd2_win':'rd6_win'] # Not advance to same
        hloss=1-higher.loc[:,'rd3_win':'rd7_win'] # Not advance further

        
        #Calculate the current team, higher and lower seed terms for rounds 2-champ
        for i in range(5):
        
            # Probability of all worse teams winning less, and all better teams winning the same or less
            lprobs[i]=np.prod(lloss.iloc[:,i].values)
            hprobs[i]=np.prod(hloss.iloc[:,i].values)
        
            # Probability of team winning exactly 1 or 2 or 3 or 4 games
            probs[i]=current.iloc[:,i+5].values[0]-current.iloc[:,i+6].values[0]
     
          

            #determine prob for no same seed: only winner
            same_loss=1-np.sum(same_probs[:,i:],axis=1)   #prob of losing before round for each team
            same_win=same_probs[:,i] # probability of each team winning the exact same number of games
            only[i]=permute(same_loss, same_win, len(same_probs[:,0]),0)
            tie1[i]=permute(same_loss, same_win, len(same_probs[:,0]),1)
            tie2[i]=permute(same_loss, same_win, len(same_probs[:,0]),2)
            tie3[i]=permute(same_loss, same_win, len(same_probs[:,0]),3)

            
            
        # Probability of winning is given by probability of winning X games * probability of worse teams winning less than X games times probability of better teams winning X games or less * (probability of same teams winning less than X games + .5 * probability of same teams winning X games), where the .5 is from assuming a split or equal odds on score differential if there is a tiebreaker

        for i in range(5):    
            prob=prob+probs[i]*lprobs[i]*hprobs[i]*only[i]
            probt1=probt1+probs[i]*lprobs[i]*hprobs[i]*tie1[i]
            probt2=probt2+probs[i]*lprobs[i]*hprobs[i]*tie2[i]
            probt3=probt3+probs[i]*lprobs[i]*hprobs[i]*tie3[i]

        
        df9['only_odds'].values[j]=prob
        df9['tie1_odds'].values[j]=probt1
        df9['tie2_odds'].values[j]=probt2
        df9['tie3_odds'].values[j]=probt3
        j=j+1
     

        
 #############################################################    

# Read in full excel sheet, get 538 sheet
df = pd.read_excel('ncaa.xlsx', sheet_name='538')

# Reset odds

df['only_odds'] = 0
df['tie1_odds'] = 0
df['tie2_odds'] = 0
df['tie3_odds'] = 0

# Get rid of a and b for play in teams, convert to numbers
#df['team_seed'] = [seed[:2] for seed in df['team_seed']] 
#df['team_seed']=df['team_seed'].apply(pd.to_numeric)
df.loc[:,'tie1_odds':'only_odds']=df.loc[:,'tie1_odds':'only_odds'].astype(float)


#Isolate 9-12 and 13-16 seeds
df9=df[(df['team_seed'] >=9) & (df['team_seed'] <= 12)][:]
df13=df[df['team_seed'] >=13][:]
df_low=df[df['team_seed'] < 9]





# Find probability of being last seed standing
get_prob(df13)
get_prob(df9)

frames=[df_low, df9, df13]
df=pd.concat(frames)



# Read in dict or df with cost per team
df2 = pd.read_excel('ncaa.xlsx', sheet_name='Draft_results')

# sort both by team name

df=df.sort_values('team_name')
df2=df2.sort_values('team_name')


df['cost']=df2['cost'].values

df['cost']=df['cost'].astype(float)
df=df.sort_values('team_rating',ascending=False)


# reorganize so that order matches normal sheet, and set to 0 for all other teams
# Write back to sheet

book = load_workbook('ncaa.xlsx')
writer = pd.ExcelWriter('ncaa.xlsx', engine='openpyxl') 
writer.book = book
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

df.to_excel(writer, '538')

print('success')
writer.save()


