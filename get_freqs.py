
import bs4
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re
import sys
from string import digits

def get_freqs():
    url="http://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom"
    html=urlopen(url)
    soup =bs(html,'html.parser')
    headers=[th.getText() for th in soup.findAll('tr')[0].findAll('th')]
    data_rows = soup.findAll('tr')
    perc = [[td.getText().split('-')[-1][:-1] for td in
             data_rows[i].findAll('td')] for i in range(len(data_rows))]
    remove_digits = str.maketrans('', '', digits)
    indeces= [[str(td.getText().split('-')[0]).translate(remove_digits)
               for td in data_rows[i].findAll('td')]
              for i in range(len(data_rows))]
    percs=pd.DataFrame(perc,columns=headers)
    names=pd.DataFrame(indeces,columns=headers)
    hold=pd.DataFrame(index=names.iloc[1:,0])

    for i in range(6):
        temp=percs.iloc[1:,i]
        temp.index=names.iloc[1:,i]
        hold=pd.concat([hold,temp], axis=1)


    results=hold[:].apply(pd.to_numeric, errors='ignore').sort_values('NCG',ascending=False)/100.
    results= results.sort_index()

    f38 = pd.read_csv('538.csv', index_col=0).set_index('team_name')
    test_names = results.join(f38)
    name1 = []
    name2 = []
    for team in results.index:
        if team not in f38.index:
            name1.append(team)
    # for team in f38.index:
    #     if team not in results.index:
    #         if team not in ['Rutgers', 'Wyoming', 'Texas A&M-Corpus Christi', 'Bryant']:
    #             name2.append(team)

    #tt = pd.DataFrame()
    #tt['538'] = name2
    #tt['ESPN'] = name1
    #breakpoint()


    name_converter = pd.read_csv('team_names.csv', index_col=0)
    espn = name_converter.set_index('ESPN')
    change = results.loc[name1].join(espn)

    idx=np.where(results.index.isin(name1))
    names = results.index.values
    names[idx] = change['538'].values
    results.index = names

    slots = f38['team_slot']
    results=results.join(slots).sort_values('team_slot')
    return results
