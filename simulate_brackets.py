# python2 simulate_brackets.py [website] nTeams=nTeams

# Can only accept nTeams to the power of 2. If mid round, do the amount before
# the round started (it will zero the rating of eliminated teams)

import numpy as np
import pandas as pd
import random
import sys
import matplotlib.pyplot as plt
from tqdm import trange


# Function that finds probability of winning game given power ratings
def get_prob(delta_rat):
    return 1/(1.0 + 10**(-1*delta_rat*30.464/400.))

# Function to simulate which teams advance.
def simulate_games(teams):
    index=list(teams.index)
    lose=[]
    # Iterate through every other team and determine probability
    # of first team winning
    for i in range(0,len(teams),2):
        delta_rat=teams.iloc[i,1]-teams.iloc[i+1,1]
        prob_team1=get_prob(delta_rat)
        test=random.uniform(0, 1)
        if test < prob_team1:
            lose.append(index[i+1])
        else:
            lose.append(index[i])
    teams=teams.drop(lose)
    # Adjust rating here for hot simulation!
    return teams

# Function that simulates points for each player given who wins the
# games. Outputs dataframe with player name and total points (in order)

def simulation(survivors, brackets, nRounds):
    # nRounds are the amount of rounds remaining. 4 for sweet 16,
    # 3 for elite 8, etc.
 
    # Simulate winners of each round for 1 run
    sim = pd.DataFrame()
    for i in range(nRounds):
        survivors = simulate_games(survivors)
        sim = sim.append(survivors)
    sim_winners = sim['matchups']
    # Append winners to bracket pool array
    
    nPlayers = len(brackets) // 63
    for i in range(nPlayers):
        brackets.iloc[63*i:63*(i+1), 4][-2**nRounds+1:] = sim_winners

    brackets['Correct?'] = (brackets['Picks'] == brackets['Winner'])
    brackets['Points'] = brackets['Round'] * brackets['Correct?']
    results = pd.DataFrame()
    ptest = []
    rtest = []
    for i in range(nPlayers): 
        ptest.append(brackets.iloc[63*i,1])
        rtest.append(brackets.iloc[63*i:63*(i+1),-2].sum())
        brackets.iloc[63*i:63*(i+1),-1]=brackets.iloc[63*i:63*(i+1),-2].sum()
    results['Player']=ptest
    results['Points']=rtest
    return results.sort_values(by='Points', ascending=False)

def get_hists(df, player, payouts, direct):
    # First get lists of point, rank and money for the player
    points=df[df['Player']==player].loc[:,'Points'].values
    rank=df[df['Player']==player].loc[:,'Rank'].values
    
    nPaid=len(payouts)      
    money=[0]*len(rank)
    for i in range(nPaid):
        money=[payouts[i] if rank[j] == i+1 else money[j]
               for j in range(len(rank))]

    # Then make histograms

    # Determine and save money results
    cash=[1 if item>0 else 0 for item in money]
    pwin=[1 if item==payouts[0] else 0 for item in money]
    percent_win=np.round(np.sum(pwin)/float(len(money))*100)
    percent_cash=np.round(np.sum(cash)/float(len(money))*100)
    mean_cash=np.round(np.mean(money))
    error_cash=np.round(np.std(money))

    money_info=[percent_win, percent_cash, mean_cash, error_cash]

    # Make the figures: 3 histograms on 1 page
    fig, axes = plt.subplots(nrows=3, ncols=1)
    fig.set_size_inches(8, 6)
    ax0, ax1, ax2 = axes.flatten()
    weights = np.ones_like(money)/float(len(money)) # Make height = probability
    ax0.hist(money,bins=12, weights=weights)
    ax0.set_title('Money Won Distribution', fontsize=10)
    ax0.set_xlabel('$')

    weights = np.ones_like(rank)/float(len(rank))
    ax1.hist(rank,bins=max(rank), weights=weights)
    ax1.set_title('Rank Distribution', fontsize=10)
    
    weights = np.ones_like(points)/float(len(points))
    ax2.hist(points, bins=50, weights=weights)
    ax2.set_title('Points Distribution', fontsize=10)
    ax2.set_xlabel('Points')
    fig.tight_layout()
    plt.text(0.3, 0.9, "Average won = $" + str(mean_cash)+" +/- "
             +str(error_cash),
             horizontalalignment='center',
             verticalalignment='center', fontsize=8,
             transform = ax0.transAxes)
    plt.text(0.3, 0.78,"Freq. of cashing: " + str(percent_cash) + "%",
             horizontalalignment='center',
             verticalalignment='center', fontsize=8,
             transform = ax0.transAxes)
    plt.text(0.3, 0.66,"Freq. of winning: " + str(percent_win) + "%",
             horizontalalignment='center',
             verticalalignment='center', fontsize=8,
             transform = ax0.transAxes)
    player=player.replace('/','')
    fig.savefig(direct+player+'_chances.png')
    #  plt.show()
    fig.clf()
    plt.clf()
    plt.close(fig)
    return money_info


#######################################################################

if __name__ == "__main__":
    direct=str(sys.argv[1])

    # Read in brackets and probabilities
    probs=pd.read_csv('538.csv', index_col=0)
    probs = probs.set_index('team_name')
    brackets=pd.read_csv(direct+'/bracket_data.csv')
    
    # brackets = pd.read_csv('./mock_bracket_pools.csv', index_col=[0,1]).loc[0]
    # npools = brackets.index[-1][0]
    # for i in range(npools):
    #     pool = brackets.loc[i]

    if direct == 'yahoo':
        payouts=[120, 60, 35, 15]
    elif direct == 'espn':
        payouts=[220, 110, 70, 40]
    elif direct=='sim':
        payouts=[150, 70, 30, 20]  
    else:
        sys.exit('Provide website')
    
    # Determine the amount of teams left
    if len(sys.argv) == 3:
        nTeams=int(sys.argv[2])
    else:
        nTeams=int(probs['team_alive'].sum())

    nRounds = int(np.log(nTeams)/np.log(2))
    # Make sure team names match between 538 and ESPN brackets
    # Update team_name index
   # a=set(brackets['Picks'])
   # b=set(probs['team_name'])
   # for i in b:
   #     if i not in a:
   #         print i

    #l=probs.index[probs['team_name']=='Loyola (IL)'][0]
        

    pick_names = pd.unique(brackets['Picks'].values)
    #test_names = results.join(f38)
    teama=[]
    for team in probs.index:
        if team not in pick_names:
            teama.append(team)


    name_converter = pd.read_csv('team_names.csv', index_col=0)
    espn = name_converter.set_index('538')
    change = probs.loc[teama].join(espn, how='inner')
    idx=np.where(probs.index.isin(change.index))
    names = probs.index.values
    names[idx] = change['ESPN'].values
    probs.index = names
    probs = probs.reset_index()
    probs = probs.rename({'index':'team_name'}, axis=1)

    # Hack to simulate pre-tourney bracket pool (combined with pre-tourney
    # 538.
    # survivors = probs.copy()
    # survivors = survivors.sort_values('team_slot')
    # survivors = survivors[survivors['team_alive']==1].loc[:, 'team_name':'team_rating']
    # survivors = survivors.rename({'team_name': 'matchups', 'team_rating':'ratings'}, axis=1)
    # breakpoint()
    #survivors = survivors.iloc[0:nTeams-1, 'team_name':'team_rating']
    
    alive=probs.loc[0:nTeams-1, 'team_alive']
    probs=probs.loc[0:nTeams-1, 'team_name':'team_rating']
    probs['team_alive']=alive
    probs['team_rating'].values[probs['team_alive']==0] = 0

    # For middle of round simulation (e.g, day 1 of sweet 16),
    # list teams that lost day 1 here so ensure they lose in
    # simulation 100% of the time (this is automated in the line
    # above, so ignore.
    # breakpoint()
    # losers = ''
    # losers=['Texas Tech', 'Arizona', 'Gonzaga', 'Michigan']
    # # probs.loc[probs.loc[:, 'team_name']=='Gonzaga', 'team_rating']=140

    # if len(losers) > 0:
    #     probs.loc[probs.loc[:, 'team_name'].isin(losers), 'team_rating'] = 0



    probs=probs.drop(columns=['team_alive'])


    # Make dataframe containing only remaining teams and power ratings
    survivors=pd.DataFrame()
    survivors['matchups']=brackets['Winner'][64-2*nTeams:64-nTeams]
    survivors['ratings']=[probs[probs['team_name']==team]['team_rating'].values[0] for team in survivors['matchups']]

    
    # Define empty dataframe and number of runs
    results = pd.DataFrame()
    nPlayers = len(brackets['Bracket Name'].drop_duplicates())
    nSim = 3000
    #if direct == 'yahoo': nPlayers=nPlayers+2
    rank = list(range(1, nPlayers+1))

    # Monte carlo simulation
    for i in trange(nSim):
        run = simulation(survivors, brackets, nRounds)
        run['Rank'] = rank
        results=results.append(run)

    # Now plot results. Get list of player names
    results=results.sort_values(by='Player')
    players=results['Player'].drop_duplicates()

    #Remove annoying ASCII characters name
    #if direct == 'yahoo': players=players[:-1]
    # Get histogram of money, points, and rank for each person
    # ,as well as determining EV, freq of cashing, and freq of winning 
    #breakpoint()
    to_df=[]
    fig_dir=direct+'/player_chances/'
    for play in players:
        cash=[play]+get_hists(results, play, payouts, fig_dir)
        print(play)
        to_df.append(cash)
 
    
    # DF for frequency of making money for each player
    money=pd.DataFrame(to_df, columns=['Player', 'Win Frequency',
                                       'Cash Frequency', 'EV', '1sigma'])
    money=money[:].apply(pd.to_numeric, errors='ignore')

    # Sort by freq of winning
    money=money.sort_values('EV', ascending=False)
    money.iloc[:,1:3]=money.iloc[:,1:3]/100.

    # Save as csv file
    money.to_csv(fig_dir+'Expected_Results.csv')

