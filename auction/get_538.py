import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
import pandas as pd
from openpyxl import load_workbook
from datetime import date, timedelta
# Script to download CSV file from 538, save it to '538' sheet of gambling excel

# Download CSV



CSV_URL='https://projects.fivethirtyeight.com/march-madness-api/2022/fivethirtyeight_ncaa_forecasts.csv'

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')

# Convert to dataframe

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    head=my_list[0]
    #my_list=my_list
    df=pd.DataFrame(my_list, columns=head)



#Extract current date predictions

today =date.today()
yesterday = str(today - timedelta(1))
#yesterday=str(today)





# Order by team ID. Extract team, rating, team seed, play in flag, rd1-rd7 win odds
#remove

df = df[(df['forecast_date'] == yesterday) & (df['gender'] == 'mens')]
#df=df.sort_values('team_id')


df=df.drop(columns=['gender', 'forecast_date', 'playin_flag',  'team_region'])
cols = df.columns.tolist()

cols=cols[-4:]+cols[:-4]
df=df[cols]
df['team_seed'] = [seed[:2] for seed in df['team_seed']] 
df=df[:].apply(pd.to_numeric, errors='ignore')

#df['ev']=(df.iloc[:,5]-df.iloc[:,6])*.005
pays=[0, .005,.015,.035,.075,.155,.355]
hold=0
wins=0

for i in range(6):
    hold=hold+(df.iloc[:,i+4]-df.iloc[:,i+5])*pays[i]
    wins+=df.iloc[:,i+4]-df.iloc[:,i+5]
df['ev']=hold+df.iloc[:,10]*pays[-1]
cols=df.columns.tolist()
hold=cols[1:-1]
cols[1]=cols[-1]
cols[2:]=hold
df=df[cols]

df=df.sort_values('team_slot')
# Write to the sheet in excel
book = load_workbook('ncaa_2021.xlsx')
writer = pd.ExcelWriter('ncaa_2021.xlsx', engine='openpyxl')
writer.book = book
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
df.to_excel(writer, "538_old")

writer.save()
