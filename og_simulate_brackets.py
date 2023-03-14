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
    return teams

# Function that simulates points for each player given who wins the
# games. Outputs dataframe with player name and total points (in order)

def simulation(survivors, brackets, nRounds):
    # nRounds are the amount of rounds remaining. 4 for sweet 16,
    # 3 for elite 8, etc.
 
    # Simulate winners of each round for 1 run
    sim=pd.DataFrame()
    for i in range(nRounds):
        survivors=simulate_games(survivors)
        survivors['Round']=i+1
        sim=sim.append(survivors)
    # sim_winners=sim.loc[:, 'matchups']
    results = sim.drop('ratings', axis=1).set_index('Round')
    # Append winners to bracket pool array
    
    # nPlayers=len(brackets)//63
    # for i in range(nPlayers):
    #     brackets.iloc[63*i:63*(i+1), 2]=sim_winners.values

    # brackets.loc[:, 'Correct?'] = (brackets.loc[:, 'Picks'] == brackets.loc[:, 'Winner'])
    # brackets.loc[:, 'Points'] = 2**(brackets.loc[:, 'Round']-1)*brackets.loc[:, 'Correct?']

    # results=pd.DataFrame()
    # ptest=[]
    # rtest=[]
    # for i in range(nPlayers): 
    #     ptest.append(brackets.iloc[63*i, :].name)
    #     rtest.append(brackets.iloc[63*i:63*(i+1), -2].sum())
    #     brackets.iloc[63*i:63*(i+1), -1] = brackets.iloc[63*i:63*(i+1), -2].sum()
    # results.loc[:, 'Player']=ptest
    # results.loc[:, 'Points']=rtest
    return results
    #return results.sort_values(by='Points', ascending=False)

def get_hists(df, player, payouts, direct):
    # First get lists of point, rank and money for the player
    points=df[df['Player']==player].loc[:,'Points'].values
    rank=df[df['Player']==player].loc[:,'Rank'].values

    nPaid=len(payouts)      
    money=[0]*len(rank)
    for i in range(nPaid):
        money=[payouts[i] if rank[j] == i+1 else money[j]
               for j in range(len(rank))]

    np.mean(money)
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
    # fig, axes = plt.subplots(nrows=3, ncols=1)
    # fig.set_size_inches(8, 6)
    # ax0, ax1, ax2 = axes.flatten()
    # weights = np.ones_like(money)/float(len(money)) # Make height = probability
    # ax0.hist(money,bins=12, weights=weights)
    # ax0.set_title('Money Won Distribution', fontsize=10)
    # ax0.set_xlabel('$')

    # weights = np.ones_like(rank)/float(len(rank))
    # ax1.hist(rank,bins=max(rank), weights=weights)
    # ax1.set_title('Rank Distribution', fontsize=10)
    
    # weights = np.ones_like(points)/float(len(points))
    # ax2.hist(points, bins=50, weights=weights)
    # ax2.set_title('Points Distribution', fontsize=10)
    # ax2.set_xlabel('Points')
    # fig.tight_layout()
    # plt.text(0.3, 0.9, "Average won = $" + str(mean_cash)+" +/- "
    #          +str(error_cash),
    #          horizontalalignment='center',
    #          verticalalignment='center', fontsize=8,
    #          transform = ax0.transAxes)
    # plt.text(0.3, 0.78,"Freq. of cashing: " + str(percent_cash) + "%",
    #          horizontalalignment='center',
    #          verticalalignment='center', fontsize=8,
    #          transform = ax0.transAxes)
    # plt.text(0.3, 0.66,"Freq. of winning: " + str(percent_win) + "%",
    #          horizontalalignment='center',
    #          verticalalignment='center', fontsize=8,
    #          transform = ax0.transAxes)
    # fig.savefig(direct+str(player)+'_chances.png')
    # # plt.show()
    # fig.clf()
    # plt.clf()
    return money_info


#######################################################################

if __name__ == "__main__":
    direct=str(sys.argv[1])

    # Read in brackets and probabilities
    probs=pd.read_csv('538b.csv')
    probs = probs[probs['team_name']!='Drake']
    probs = probs[probs['team_name']!='Appalachian State']
    probs = probs[probs['team_name']!='UCLA']
    probs = probs[probs['team_name']!='Texas Southern']
    #brackets=pd.read_csv(direct+'/bracket_data.csv')

    if direct == 'yahoo':
        payouts=[175, 100, 65, 40, 20]
    elif direct == 'espn':
        payouts=[160, 90, 60, 30]
    elif direct=='sim':
        payouts=[240, 100, 50, 30]
    else:
        sys.exit('Provide website')
    
    # Determine the amount of teams left
    if len(sys.argv) == 3:
        nTeams=int(sys.argv[2])
    else:
        nTeams=int(probs['team_alive'].sum())

    nRounds=int(np.log(nTeams)/np.log(2))

    # Make sure team names match between 538 and ESPN brackets
    # Update team_name index
   # l=probs.index[probs['team_name']=='Loyola (IL)'][0]

    alive=probs.loc[:, 'team_alive']
    probs=probs.loc[:, 'team_name':'team_rating']
    probs['team_alive']=alive
    probs['team_rating'].values[probs['team_alive'] == 0]=0
    probs=probs.drop(columns=['team_alive'])
    
    # Make dataframe containing only remaining teams and power ratings

    survivors=pd.DataFrame()
    match=pd.read_csv('matchups.csv', index_col=0)
    #  survivors['matchups']=brackets['Winner'][64-2*nTeams:64-nTeams]
    survivors['matchups']=match.index.values
    survivors['ratings']=[probs[probs['team_name']==team][
        'team_rating'].values[0] for team in survivors['matchups']]


    pools = pd.read_csv('./mock_bracket_pools.csv', index_col=[0, 1])
    pools.loc[:, 'Winner'] = pools.loc[:, 'Winner'].astype('str')
    #npools = pools.index[-1][0]
    npools=1
    nSim=50000
    all_cash = pd.DataFrame()
    for j in range(npools):
        brackets = pools.loc[j]
        #picks= brackets.copy()
        #picks = picks.reset_index().set_index('Round')
        #winners = picks.loc[6, 'Picks'].values
        #finalists = picks.loc[5, 'Picks'].values
        #finalists = finalists.reshape(len(finalists)//2, 2)
        #final4 = picks.loc[4, 'Picks'].values
        #final4 = final4.reshape(len(final4)//4, 4)
        # Define empty dataframe and number of runs
        results=pd.DataFrame()
        #nPlayers=brackets.index[-1]
        #rank=range(1,nPlayers+2)
        # Monte carlo simulation
        for i in trange(nSim):
            run=simulation(survivors, brackets, nRounds)
            #run.loc[:, 'Rank']=rank
            run.loc[:,'run']=i
            results=results.append(run)

        breakpoint()
        results.to_csv('sim50000b.csv')
        results=results.sort_values(by='Player')
        players=results['Player'].drop_duplicates()

        # Get histogram of money, points, and rank for each person
        # ,as well as determining EV, freq of cashing, and freq of winning 

        to_df = []
        fig_dir = direct + '/'
        
        for play in players:
            cash=[play]+get_hists(results, play, payouts, fig_dir)
            to_df.append(cash)
 
        # DF for frequency of making money for each player
        money=pd.DataFrame(to_df, columns=['bracket_id', 'Win Frequency',
                                           'Cash Frequency', 'EV', '1sigma'])
        money=money[:].apply(pd.to_numeric, errors='ignore')

        # Sort by EV
        money=money.sort_values('EV', ascending=False)
        money.iloc[:,1:3]=money.iloc[:,1:3]/100.
        money=money.reset_index().drop('index', axis=1)
        money['pool_id'] = j
        money.loc[:, ['f4w', 'f4e', 'f4mw', 'f4s']]=final4
        money.loc[:, ['f1', 'f2']] = finalists
        money.loc[:, 'winner'] = winners

        all_cash = all_cash.append(money)
    # Save as csv file
    all_cash = all_cash.set_index('pool_id')
    all_cash.to_csv(fig_dir+'expected_results.csv')
    

