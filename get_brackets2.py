# Program that reads every bracket in the pool into a dataframe. This includes bracket
# name, future picks, results, right/wrong for each game, point values for each game,
# And total points for the bracket.

# Fill in future results for each dataframe to "generate scenarios" 

from urllib2 import urlopen
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re
import sys



n=5
pts=np.zeros(63)
for i in range(63):
    if 64-i > 2**n:
        pts[i]=2**(5-n)
    if 64-i == 2**n:
        n=n-1
        pts[i]=2**(5-n)

####################################################################################
########################### Now do for all brackets  ########################
####################################################################################

url_temp="http://games.espn.com/tournament-challenge-bracket/2019/en/entry?entryID={id}"

ids=[15896004, 15955448,12961050,14599786, 15768336, 13890568]
ids=[26469006,26723636,26618868,26626033,29486936,34538522,23894965
     ,31566637,35499882,32824870]

ids=[str(item) for item in ids]

# Empty data frame

group_df=pd.DataFrame()


for item in ids:

    url=url_temp.format(id=item)
    html=urlopen(url)

    soup =bs(html,'html.parser')

    choice=soup.find_all(class_=re.compile('selectedTo'))
    pick=[cho.find_all(class_=re.compile('name'))[0].getText() for cho in choice]
    del pick[-4]

    win=soup.find_all(class_=re.compile('winner'))
    wins=[cho.find_all(class_=re.compile('name'))[0].getText() for cho in win]
    # wins=[it.getText() for it in win]
    w=pd.Series(wins)
    name=soup.find_all(class_=re.compile('entryname'))[0].getText()
    name=name.encode('utf-8')

    player_df = pd.DataFrame({'Bracket Name': name, 'Picks':pick,'Round':pts})
    player_df['Winner']=w
    player_df.fillna(0, inplace=True)
  
    player_df['Correct?']=(player_df['Picks'] == player_df['Winner'])
    player_df['Points']=player_df['Round']*player_df['Correct?']
    player_df['Total']= player_df['Points'].sum()


    group_df=group_df.append(player_df, ignore_index=True)
    print 'One bracket done'

group_df.to_csv('./espn/bracket_data2.csv')

