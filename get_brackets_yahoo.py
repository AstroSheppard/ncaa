# Program that reads every bracket in the pool into a dataframe. This includes bracket
# name, future picks, results, right/wrong for each game, point values for each game,
# And total points for the bracket.

# Fill in future results for each dataframe to "generate scenarios" 

from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re
import sys


n=5
pts=np.zeros(63)
wins=[]

for i in range(63):
    if 64-i > 2**n:
        pts[i]=2**(5-n)
    if 64-i == 2**n:
        n=n-1
        pts[i]=2**(5-n)

url_temp="https://tournament.fantasysports.yahoo.com/t1/{id}"
template="region-{i}-round-{j}"
#item='55610'
#item='64015'
item='1667159'
url=url_temp.format(id=item)
html=urlopen(url)

soup = bs(html,'html.parser')

breakpoint()
for i in range(1,4):
    for j in range(1,5):
        
        r=soup.findAll("fieldset", {"id":template.format(i=str(j), j=str(i))})
          

        win=r[0].find_all(class_=re.compile('ysf-tpe-actual-pick'))
        test2=[cho.find_all('b')[0].getText()[2:].lstrip() for cho in win]
        wins=wins+test2
j=0
for i in range(4,7):
    r=soup.findAll("fieldset", {"id":template.format(i=str(j), j=str(i))})
              
    win=r[0].find_all(class_=re.compile('ysf-tpe-actual-pick'))
    test2=[cho.find_all('b')[0].getText()[2:].lstrip() for cho in win]
    wins=wins+test2

  
w=pd.Series(wins)

########################### Now do for all brackets  ########################
####################################################################################

url_temp="https://tournament.fantasysports.yahoo.com/t1/{id}"
#ids=[1322129,961201,115881,2137892,54518,39050,55610,633414,2115096,2234199,892373,1843168,635316,341797,569454,2006375,2192584,1037046,594977,619340,1996602,1016275,2013463, 1457983,756043, 139984,2009388, 1750992, 1389947, 1108595, 52731, 2164940, 1387464, 1727457, 2337317, 1309242, 1423002, 135028, 2025237, 1078686, 1314978, 2151622]
# #ids=[3066146,2503743,2297880,2606209,2397307,2447379,2842261,2099791,478220
#      ,1857189,304445,2933252,3086231,461485,1024358,425869,718719,779150
#      ,3073780,2648674,2913616,1571132,2523412,2607447,1988631,1517805,2114878
#      ,3156638,2228150,1836013,2637475,2113478,731244,2124358,2504855]
#ids=['55610']
#ids = [1101771, 1123486, 140478, 1471288, 273511, 1066451, 138497
#       , 594648, 1199857, 736074, 140514, 1356258, 1356258,
#       225625, 1055708, 652002, 951874]
ids = [1667159, 346800, 1628317, 315262, 1581465, 675530, 378025
       , 812611, 1101194, 863371, 1116918, 151881, 286726, 1465642
       , 1466896, 1737117, 1544863, 1655071, 1040740, 776281, 210536
       , 1568633, 285415]
ids=[str(item) for item in ids]

# Empty data frame

group_df=pd.DataFrame()

for item in ids:

    url=url_temp.format(id=item)
    html=urlopen(url)

    soup =bs(html,'html.parser')
    pick=[]
    template="region-{i}-round-{j}"
    for i in range(1,4):
        for j in range(1,5):
            
            r=soup.findAll("fieldset", {"id":template.format(i=str(j), j=str(i))})
    
            choice=r[0].find_all(class_=re.compile('ysf-tpe-user-pick'))
            test=[cho.find_all('b')[0].getText()[2:].lstrip() for cho in choice]
            pick=pick+test

     
    j=0
    for i in range(4,7):
        r=soup.findAll("fieldset", {"id":template.format(i=str(j), j=str(i))})
    
        choice=r[0].find_all(class_=re.compile('ysf-tpe-user-pick'))
        test=[cho.find_all('b')[0].getText()[2:].lstrip() for cho in choice]
        pick=pick+test

    
    name=soup.find_all(class_=re.compile('Fz-xxl Mend-med'))[0].getText()
    name=name.encode('utf-8')
 
    player_df = pd.DataFrame({'Bracket Name': name, 'Picks':pick,'Round':pts})
    player_df['Winner']=w
    player_df.fillna(0, inplace=True)
  
    player_df['Correct?']=(player_df['Picks'] == player_df['Winner'])
    player_df['Points']=player_df['Round']*player_df['Correct?']
    player_df['Total']= player_df['Points'].sum()


    group_df=group_df.append(player_df, ignore_index=True)
    print(item)
print(group_df)

group_df.to_csv('./yahoo/bracket_data.csv')

