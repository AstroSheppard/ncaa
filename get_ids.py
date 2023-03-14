import sys
import pandas
from bs4 import BeautifulSoup as bs
from urllib2 import urlopen
import re
import numpy as np

url_temp="https://tournament.fantasysports.yahoo.com/t1/group/{id}"
id=sys.argv[1]
url=url_temp.format(id=id)
html=urlopen(url)
soup =bs(html,'html.parser')
headers=[th.getText() for th in soup.findAll('tr')[0].findAll('th')]
data_rows = soup.findAll('tr')
past = [[td.getText() for td in data_rows[i].findAll('td')]
        for i in range(len(data_rows))]
print past
