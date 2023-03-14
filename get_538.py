import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
import pandas as pd
from datetime import date, timedelta
import sys
# Script to download CSV file from 538, alter data a bit, and save it to csv



CSV_URL='https://projects.fivethirtyeight.com/march-madness-api/2022/fivethirtyeight_ncaa_forecasts.csv'

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')

# Convert to dataframe

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    head=my_list[0]
    df=pd.DataFrame(my_list, columns=head)

#Extract current date predictions
days=int(sys.argv[1])
today = date.today()
yesterday = str(today - timedelta(days))

# Order by team ID. Extract team, rating, team seed, play in flag,
#rd1-rd7 win odds 

df = df[(df['forecast_date']==yesterday) & (df['gender']=='mens')]

df=df.drop(columns=['gender', 'forecast_date', 'playin_flag', 'team_region'])

cols = df.columns.tolist()

cols = cols[-4:]+cols[:-4]
df = df[cols]
df['team_seed'] = [seed[:2] for seed in df['team_seed']]

df = df[:].apply(pd.to_numeric, errors='ignore')
df.to_csv("538.csv")


