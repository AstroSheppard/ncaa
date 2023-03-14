# Program that reads every bracket in the pool into a dataframe.
# This includes bracket name, future picks, results, right/wrong
# for each game, point values for each game, And total points for
# the bracket.

# Fill in future results for each dataframe to "generate scenarios" 

from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re
import sys
from tqdm import tqdm

n=5
pts=np.zeros(63)
for i in range(63):
    if 64-i > 2**n:
        pts[i]=2**(5-n)
    if 64-i == 2**n:
        n=n-1
        pts[i]=2**(5-n)

#############################################################################
########################### Now do for all brackets  ########################
#############################################################################

url_temp="http://games.espn.com/tournament-challenge-bracket/2022/en/entry?entryID={id}"

#ids=[20178183, 33714884, 19510517,26870787,35085428,19071884,29869289,19639658
     # ,25957914,19106773,25818755,19421484,24542429,19084807,20426603,27605426
     # ,19282867,24669006,20253772,27642540,33593490,19018959,32512132,22200192
     # ,27085581,29525270,33576793,33592114,32962047]

# ids = [49019560, 38023068, 40128095, 38816664, 44809454, 52322624,
#        49304307, 38505994, 51972732, 37438137, 38221072, 38877258,
#        43007243, 51829105, 38039234, 51348499, 50403615, 49307150,
#        43319722, 38705429, 50373573, 51597236, 45537714, 45874884,
#        37437641, 50039484, 43611342, 49337490]

ids = [55130915, 58441937, 62336472, 63997503, 59411495, 65088601
       , 57002362, 65904994, 71353538, 58365328, 66602047, 62638332
       , 56681073, 69378462, 56481738, 53735721, 54349322, 59399962
       , 53735739, 68667832, 61857514]
ids=[str(item) for item in ids]

# Empty data frame

group_df = pd.DataFrame()

for item in tqdm(ids):

    url=url_temp.format(id=item)
    html=urlopen(url)

    soup = bs(html,'html.parser')
    choice=soup.find_all(class_=re.compile('selectedTo'))
    pick=[cho.find_all(class_=re.compile('name'))[0].getText()
          for cho in choice]
    del pick[-4]

    win=soup.find_all(class_=re.compile('winner'))
    wins=[cho.find_all(class_=re.compile('name'))[0].getText() for cho in win]
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

group_df.to_csv('./espn/bracket_data.csv')

