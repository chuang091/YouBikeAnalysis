import datetime
import pandas as pd
import numpy as np
import requests
import json
from pandas import json_normalize
import time
flag=True
k=0
print('start')
while flag:
    Youbike_url = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'
    r = requests.get(Youbike_url)
    data = r.json()
    x_df = json_normalize(data)
    current_datetime = datetime.datetime.now()
    save_file_name = '{}_data.csv'.format(current_datetime.strftime('%Y-%m-%d_%H-%M-%S'))
    x_df.to_csv(save_file_name, encoding='utf-8', index=False)
    print(k)
    time.sleep(60)
    k+=1
    if k==1440 : flag=False
