import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
import pandas as pd
from get_freqs import get_freqs as gf
#from openpyxl import load_workbook
from datetime import date, timedelta
import sys

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

# Order by team ID. Extract team, rating, team seed, play in flag, rd1-rd7 win odds
#remove

df = df[(df['forecast_date'] == yesterday) & (df['gender'] == 'mens')]
#df=df.sort_values('team_id')


df=df.drop(columns=['gender', 'forecast_date', 'playin_flag',  'team_region', 'team_rating', 'rd1_win'])

cols = df.columns.tolist()

cols=cols[-4:]+cols[:-4]
df=df[cols]
#df['team_seed'] = [seed[:2] for seed in df['team_seed']] 
df=df[:].apply(pd.to_numeric, errors='ignore')
df=df.set_index('team_slot')
#df=df['rd7_win']


freqs=gf()

#freqs.loc['NDS']=freqs.loc['NDS/NCC']/2.
#freqs.loc['NDS', 'team_slot']=2
#freqs.loc['NCC']=freqs.loc['NDS/NCC']/2.
#freqs.loc['NCC', 'team_slot']=3
#freqs.loc['SJU']=freqs.loc['ASU/SJU']/2.
#freqs.loc['SJU', 'team_slot']=51
#freqs.loc['ASU']=freqs.loc['ASU/SJU']/2.
#freqs.loc['ASU', 'team_slot']=50
#freqs=freqs.drop(['ASU/SJU'], axis=0)
#freqs=freqs.set_index('team_slot')
df=df.set_index('team_name')
total=df.join(freqs).dropna().sort_index()
# breakpoint()

rd=int(sys.argv[1])
total=total[total.iloc[:,10+rd]!=0]
total=total[total.iloc[:,2+rd]!=0]
power=float(sys.argv[2])
if len(sys.argv)==5:
    s1=int(sys.argv[3])
    s2=int(sys.argv[4])
    total=total[total.index>=s1]
    total=total[total.index<=s2]

ems1=[]
ems2=[]
total=total.sort_values('team_slot')
for j in range(len(total.index)):
    sum1=0
    sum2=0
    for i in range(len(total.index)):
        # Get the point total for the round
        # (1 - freq picked) * odds to win * pts / (freq picked) ^ power
        #hold1=((i==j)-total.iloc[i,10+rd])*total.iloc[i,2+rd]*2**rd/(total.iloc[i,10+rd]**power)
        # -Freq of team i picked to win * odds of winning * pts 
        hold2=((i==j)-total.iloc[i,10+rd])*total.iloc[i,2+rd]*2**rd
        hold1=(1+(total.iloc[i, 2+rd] - total.iloc[i, 10+rd]))*2**rd*total.iloc[i, 2+rd]
        #hold1=0
        if i==j:
            hold2=hold2/(total.iloc[j,10+rd])**power
            hold1=(1+(total.iloc[i, 2+rd] - total.iloc[i, 10+rd]))*2**rd*total.iloc[i, 2+rd]
        else:
            hold1=0
            #hold1 = (1 + total.iloc[i, 2+rd]
            #         - total.iloc[i,10+rd])**power*total.iloc[i,2+rd]*2**rd
            #hold=hold/(total.loc[j,'freq'])**.5
        #if j=='Virginia Tech':
            #print hold
        sum1+=hold1
        sum2+=hold2
    ems1.append(sum1)
    ems2.append(sum2)

out=pd.DataFrame(index=total.index)
out['EM1']=ems1
out['EM2']=ems2
out['odds']=total.iloc[:,2+rd]*100
out['freq']=total.iloc[:,10+rd]*100
# out['Team']=total['team_name']
out['Team']=total.index
out=out.set_index('Team').sort_values('EM1', ascending=False).round(2)

#total['factor']=total['rd7_win']/total['freq']
#total['sq']=total['rd7_win']**2/total['freq']
#total['sqrt']=total['rd7_win']/np.sqrt(total['freq'])
#total['cube']=total['rd7_win']/(total['freq']**.4)
print(out.head(55))
# Write to the sheet in excel

#book = load_workbook('ncaa.xlsx')
#writer = pd.ExcelWriter('ncaa.xlsx', engine='openpyxl', ) 
#writer.book = book
#writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

#df.to_excel(writer, "538")

#writer.save()
