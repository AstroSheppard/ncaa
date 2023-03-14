import pandas as pd
import numpy as np
import datetime
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
from urllib.request import urlopen
import matplotlib.pyplot as plt
from get_freqs import get_freqs as gf
from numpy import random
import sys

def simulate_games(teams, nRound):
    index = list(teams.index)
    lose = []
    # Iterate through every other team and determine probability
    # of first team being picked for this bracket
    for i in range(0, len(teams), 2):
        pick1 = teams.iloc[i, nRound]
        pick2 = teams.iloc[i+1, nRound]
        # Probability of winning future round matchups is not known, and
        # is unfeasible to calculate for the insane amount of combos. Only doing
        # conditional probability (p(current)/p(past) tends to overrate underdogs
        # in later rounds, since they are not 40% against top teams. Just normalizing
        # the probabilities has the opposite impact, since, e.g., UVA being likely to
        # lose to Gonzaga early on makes them lose too often later (should be like 40%
        # against top teams, not 5%). Solution? Weighted average. Conditional probability
        # is a good approximation, normalizing total probability acts as a correction
        # term to gauge the quality of the opponent. This recreates
        # bracket probabilities to within 2%. 
        if nRound != 0:
            pick1 = pick1 / teams.iloc[i, nRound-1] + pick1*min((2.5+nRound)/4, 1)
            pick2 = pick2 / teams.iloc[i+1, nRound-1] + pick2*min((2.5+nRound)/4, 1)
        norm = pick1 + pick2

        # Now get percent of time each team is picked given
        # this matchup
        prob1 = pick1 / norm
        prob2 = pick2 / norm
        assert((prob1 + prob2).round(4) == 1)
        test = random.uniform(0, 1)
        if test < prob1:
            lose.append(index[i+1])
        else:
            lose.append(index[i])
    teams=teams.drop(lose)
    # breakpoint()
    return teams

def simulation(pick_percs):
    sim = pd.DataFrame()
    picks = pick_percs.copy()
    for i in range(6):
        picks = simulate_games(picks, i)
        picks['Round'] = i + 1
        sim = sim.append(picks)
    return sim

def make_picks(nbrackets=10000, pool_size=25):
    br=pd.read_csv('mock_bracket_pools.csv', index_col=[0,1]).iloc[:nbrackets*63]
    br.reset_index(inplace=True)
    br['pool_id']=np.repeat(np.arange(0, nbrackets//pool_size), pool_size*63) 
    br['bracket_id']=np.tile(np.repeat(np.arange(0, pool_size), 63), nbrackets//pool_size)
    br.set_index(['pool_id', 'bracket_id'], inplace=True)
    pick = br.copy()
    pick.reset_index(inplace=True)
    pick.set_index('Round', inplace=True)

    npools=nbrackets//pool_size
    #pool_size += 1
    payouts=[500, 250]
    payouts=np.array(payouts)*pool_size/25
    #1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5
    sims=pd.read_csv('sim50000b.csv').iloc[:nbrackets*2*63]
    sims['game']=np.arange(63).tolist()*nbrackets*2
    sims2=sims.pivot(index='game', columns='run', values='matchups').values
    # 55 seconds for this part, near memory limit
    sims3=np.concatenate([sims2]*pool_size)
    
    # sims3=sims3.iloc[:, :500]
    points = np.empty((npools*pool_size*63, 1000))
    hold = br.loc[0].iloc[:, 0].values

    # Loop through each of the 1000 pools
    # rint = np.random(0, 49000)
    # sims3.values[:, rint:rint+1000]
    # last try: more groups (all 100x63x25 vs 20000
    # Add my bracket to each pool
    
    #mybracket = pd.read_csv('mybracket.csv')
    #mybracket['bracket_id']=99999
    #mybracket=mybracket.set_index('bracket_id')
    #hold = np.append(hold, hold[:63])
    pts = (2**(hold - 1))
    
    print('starting pool loop')
    for pool, df in br.groupby(level=0):
        print(pool)
        idx=np.random.randint(0,nbrackets*2-1000)
        sims = sims3[:, idx:idx+1000]
        # pts = (2**(df.loc[:,'Round'] - 1)).to_frame()
        #df = df.append(mybracket)
        picks = df.loc[:,'Picks'].to_frame()
        corrects = picks.values==sims
        points[(pool)*63*pool_size:(pool+1)*63*pool_size, :] = (corrects.T * pts).T
    print('points done')
    del sims3
    del sims
    points2d=pd.DataFrame(points)
    del points
    idsa=np.repeat(np.arange((points2d.index[-1]+1)/63),63)
    points2d['id']=idsa
    del idsa
    # this is the slowest part
    pts = points2d.groupby('id').sum()
    print('pts groupby done')
    idsb = np.repeat(np.arange((pts.index[-1]+1)//pool_size), pool_size)
    pts['pool'] = idsb
    ranks = pts.groupby('pool').rank(ascending=False)
    default = np.zeros_like(ranks.values)
    print('Ranks done')
    for i in range(1,3):
        default += payouts[i-1]*(ranks==(0.5*i+0.5))
        print(.5*i+.5)
    evs = default.mean(axis=1)-20
    a1 = pd.unique(br.index.get_level_values(0))
    a2 = pd.unique(br.index.get_level_values(1))
    # a2 = np.append(a2, 99999)
    index = pd.MultiIndex.from_product([a1, a2], names=["pool", "bracket"])
    money = pd.DataFrame(evs.values, index=index, columns=['EV'])
    #mine = money.unstack()
    #myev = mine.loc[:, ('EV', 99999)]
    #mybracket['mean_ev']=myev.mean()
    #print(myev.mean())
    #mybracket.to_csv('mybracket5.csv')
    #sys.exit()

    winners = pick.loc[6, 'Picks'].values
    finalists = pick.loc[5, 'Picks'].values
    finalists = finalists.reshape(len(finalists)//2, 2)
    final4 = pick.loc[4, 'Picks'].values
    final4 = final4.reshape(len(final4)//4, 4)
    elite8 = pick.loc[3, 'Picks'].values
    elite8 = elite8.reshape(len(elite8)//8, 8)
    r1 = pick.loc[1, 'Picks'].values
    r1 = r1.reshape(len(r1)//32, 32)
    r2 = pick.loc[2, 'Picks'].values
    r2 = r2.reshape(len(r2)//16, 16)
    # labs=np.arange(32).astype(str)
    labs = np.arange(16+32).astype(str)
    money.loc[:, ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8']]=elite8
    money.loc[:, ['f4w', 'f4e', 'f4mw', 'f4s']]=final4
    money.loc[:, ['f1', 'f2']] = finalists
    money.loc[:, 'winner'] = winners
    money.loc[:, labs[:32]] = r1
    money.loc[:, labs[32:]] = r2
    finals = money.groupby(['winner', 'f1', 'f2']).agg(**{'EV': ('EV', np.mean), 'n': ('EV', np.size)})
    finals = finals[finals['n']>15].sort_values('EV', ascending=False)
    winners = money.groupby(['winner']).agg(**{'EV': ('EV', np.mean), 'n': ('EV', np.size)})
    winners = winners[winners['n']>15].sort_values('EV', ascending=False)
    final4 = money.groupby(['winner', 'f1', 'f2', 'f4mw', 'f4e', 'f4s', 'f4w']).agg(**{'EV': ('EV', np.mean), 'n': ('EV', np.size)})
    final4 = final4[final4['n']>10].sort_values('EV', ascending=False)
    #tmoney=money.loc[money['winner']=='Gonzaga',:]
    #tmoney=money.loc[money['winner']=='Baylor',:]
    elite8 = money.groupby(['winner', 'f1', 'f2', 'f4mw', 'f4e', 'f4s', 'f4w', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8']).agg(**{'EV': ('EV', np.mean), 'n': ('EV', np.size)})
    elite8 = elite8[elite8['n']>10].sort_values('EV', ascending=False)
    finals.to_csv('finalist_25_winner_take_all.csv')
    final4.to_csv('final4_25_winner_take_all.csv')
    winners.to_csv('winners_25_winner_take_all.csv')
    for i in range(48):
        print(money.groupby([str(i)]).agg(**{'EV': ('EV', np.mean), 'n': ('EV', np.size)}))

    breakpoint()
        
    
def dostuff():

    pick_percentages = gf()

    pick_percentages.to_csv('freqs.csv')
    # breakpoint()
    # Alter frequencies depending on pool
    # e.g, round1 = 100 for 1 seeds
    # higher pick freq for UVA
    # Honestly do this by hand
    
    # Define empty dataframe and number of runs
    results = pd.DataFrame()
    nPlayers = 25
    nSims = 1000
    # Generate brackets

    for j in range(nSims):
        print('%.1f%%' % (j/nSims*100))
        bracket_pool = pd.DataFrame()
        for i in range(nPlayers):
            bracket = simulation(pick_percentages)
            # This should be:
            # | Bracket name | Picks | Round |
            bracket_id = '{0:03d}'.format(i)
            bracket['bracket_id'] = bracket_id
            bracket_pool = bracket_pool.append(bracket)
        pool_id = '{0:03d}'.format(j)
        bracket_pool['pool_id'] = pool_id
        results = results.append(bracket_pool)

    results = results.drop(['R64', 'R32', 'S16', 'E8'
                            , 'F4', 'NCG', 'team_slot'], axis=1)
    results = results.reset_index()
    results = results.set_index(['pool_id', 'bracket_id'])
    results['Picks'] = results['index']
    results['Winner']=0
    results['Correct?']=0
    results['Points']=0
    results['Total']=0
    results = results.drop('index', axis=1)
    breakpoint()
    results.to_csv('mock_bracket_pools.csv')

    # for i in range(1,7):
    #     winners = results[results.loc[:,'Round']==i]
    #     sim_freq = plt.hist(winners['team_slot'], bins=64, edgecolor='k')
    #     bins = sim_freq[1]
    #     plt.plot(pick_percentages['team_slot']
    #              , pick_percentages.iloc[:, i-1]*nPlayers
    #              , 'r',marker='.', ls='')
    #     plt.show()
    #     breakpoint()
    # check that bracket distribution matches ESPN percentage. Then try for
    # actual nplayers

    # Save bracket pools to "mock_bracket_pools.csv".
    # Create my own bracket to add to these
    # Use 538 probs to simulate EVs and get results 10000 or 100,000 times. Save,
    # and only rerun if probs change.

    # Use simulated results and simulated brackets to get place of my bracket and
    # winnings in each pool. Get mean winnings, and also distribution in general.
    
    # Rerun for new bracket. Track changes!

    ## Other in-between options: Generate a ton of brackets using 538 probabilities (or just sample randomly
    # from simulated results???). Only look at final 4+, and brute force every plausible combo.
    # 

    # Look for trends between input odds (parameterized by odds*freq^-x), or q-learning reinforcement
    # if feasible.


