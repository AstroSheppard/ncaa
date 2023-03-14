from get_freqs import get_freqs as gf
import numpy as np
import sys
import pandas as pd
import matplotlib.pyplot as plt

# This program takes the national frequencies and tests
# how much they can reasonably range for a certain bracket group size.
# This assumes an unbiased group (ie, not all UVA fans) and that each
# winner is picked in a bracket by using the frequency it's picked as a probability.

# That is, if team A is picked 20% nationally, then any given bracket has a 20% chance
# of picking team A. In a pool of 30 people, what range of frequencies is team A picked?


nBrackets=int(sys.argv[1])
nSims=int(sys.argv[2])
cutoff=float(sys.argv[3])
teams=gf()['NCG'].sort_values()
teams.iloc[1:5]=teams.iloc[1:5]-.001
teams=teams.cumsum()
test=np.random.random((nSims, nBrackets))
winners=np.zeros_like(test).astype(str)
breakpoint()
#winners=np.zeros(nBrackets).astype(str)

for i in range(nSims):
    for j in range(nBrackets):
        winners[i,j]=teams[(test[i,j]-teams)<0].index[0]
winners=pd.DataFrame(winners).T
#wins=pd.DataFrame()
for i in range(nSims):
    if i==0:
        wins=winners[i].value_counts()
    else:
        wins=pd.concat((wins, winners[i].value_counts()),axis=1)
wins=wins/float(nBrackets)
wins=wins.fillna(0)
wins=wins.T
contenders=wins[wins.columns[wins.quantile(.977)>cutoff]]
breakpoint()
ranges=contenders.quantile([.0223, .16, .5, .84, .977]).T*nBrackets
ranges.columns=['Min', '1sig-', 'Median', '1sig+','Max']
ranges=ranges.sort_values(['Median', '1sig+', 'Max'], ascending=False)
print(ranges.round(1))
contenders.hist()
plt.show()


# Now, for each simulated group calculate expected value for 1 extra participant
# picking each winner with freq > 1%. To do this, for each simulation pick a winner.
# Also set up payouts (payouts=np.array([150,100,65,30,15])). 
# For each winner pick, if pick == winner: same=winners[i].value_counts().loc[winner]+1
# If same>=5: payouts = nBrackets*10
# else: sum=payouts[0:same].sum()
# EV = sum/same
# Also reverse: if no one or less than 5 picked winner than EV =reverse(sum)/# non pickers

# can I ignore final 10% of low freq winners? Try to incorporate if easy. Get avg EV
# of every team and freq of being picked

# make sure to add pick to simulation


#So dataframe with all teams with freq>1% has team as index and EV from each simulation as new column (transpose this)
