import datetime
import math
import os
from matplotlib.pyplot import draw
import pandas as pd
import numpy as np
import requests
import json
from pandas import json_normalize
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import folium
import base64
import pandas as pd
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
def data_iterater(b):
    a=os.listdir(b) #獲得資料夾內檔案內容 (List)
    flag=0
    for i in a:
        try:
            if i.endswith('.csv'): #確保副檔名
                x = pd.read_csv("{a}/{x}".format(a=b, x=i), header=0)
                for k in range(len(x.loc[:]['sna'])):
                    a = x.loc[k, 'sna']
                    (x.loc[k,'sna']) = a[11:] #調整站點名稱
                x=x.drop_duplicates(subset=['sna']) #刪除重複值
                x.set_index("sna", inplace=True, drop=True) #set index
                if flag == 0:
                    y = (x[['tot', 'lat','lng','sbi']]) #初始化數據
                    y = y.rename(columns={'sbi': '{}'.format(i[11:16].replace('-',''))}) #時間中間的槓刪掉
                else:
                    z = x[['sbi']] #每個檔案都要'sbi'
                    z = z.rename(columns={'sbi': '{}'.format(i[11:16].replace('-',''))})
                    y = pd.concat([y, z], axis=1) #sbi跟初始化資料連再一起
                flag += 1 #計數器+1
        except pd.errors.EmptyDataError: #避免資料空白
            print('Note: filename.csv was empty. Skipping.')
            continue
    print('done iterate') #完成訊息
    y.to_csv("timecsv/{}時間表.csv".format(b)) #儲存資料
def draw(i):
    def plot(bike): #繪製站點圖表
        x=list(pdx.loc[bike][3:]) #List方式呈現
        tick_spacing=60 #每分鐘為一格-start
        fig, ax = plt.subplots(1,1)
        ax.plot(y,x)
        plt.xticks(y,label,rotation=45)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing)) #每分鐘為一格-end
        plt.xlabel('時間/小時',fontproperties="SimSun") #表頭
        plt.ylabel('可租借數量',fontproperties="SimSun")
        plt.title(bike,fontproperties="SimSun") 
        if not os.path.isdir('{}表格'.format(i)): os.mkdir('{}表格'.format(i)) #建立表格資料夾
        plt.savefig("{a}表格/{b}.jpg".format(a=i,b=bike)) #儲存檔案 (檔名為日期及站點名稱)
        plt.clf()
        plt.cla()
        plt.close('all') #清除目前工作內容
        del fig
    pdx = pd.read_csv("timecsv/{}時間表.csv".format(i), header=0)
    pdx.set_index("sna", inplace=True, drop=True)
    y=(list(pdx))
    y=y[3:]
    label=[int(round(float(i)))//100 for i in y] #獲取小時表
    bikedata=list(pdx.index) #取得站點列表
    fig = plt.figure()
    for j in bikedata: #跌代站點
        try:plot(j)
        except FileNotFoundError :
            print('not found')
            pass
        except MemoryError:
            time.sleep(60)
            plot(j)
            continue
    print('done for draw work!!')
def timetoloc(day):
    folder='{}表格'.format(day)
    x = pd.read_csv("timecsv/{}時間表.csv".format(day), header=0) #抓csv
    x.set_index("sna", inplace=True, drop=True)
    bikedata=list(x.index) #獲取站點資料
    def diff(x): #計算流量
        s=0
        nx = [i for i in x if math.isnan(i) == False] #清除NAN
        for i in range(len(nx)):
            if i==0:pass #pass 0
            else: s+= abs(nx[i]-nx[i-1]) #將資料差累加
        return s
    data=[]
    for i in bikedata: #跌代站點名稱
        j='{}/{}.jpg'.format(folder,i) #圖表的路徑名稱
        data.append([i,int(diff(list(x.loc[i][3:]))),j]) #二微陣列
    final=pd.DataFrame(data, columns=['sna','流量','路徑']) #建立df
    final.set_index("sna", inplace=True, drop=True) #將站點名稱作為index
    tem= (x[['tot', 'lat','lng']]) #將取得時間表的部分內容
    final = pd.concat([tem,final], axis=1) #concat
    final.to_csv("final/{}座標表.csv".format(day)) #儲存
    print('done time to loc!!')
def fo(day):
    m = folium.Map((25.0133904,121.52245),zoom_start=14) #初始化地圖內容
    folium.TileLayer('Stamen Terrain').add_to(m) #底圖
    x = pd.read_csv("final/{}座標表.csv".format(day), header=0) #讀取座標表的內容
    x.set_index("sna", inplace=True, drop=True) #index設定
    bikedata=list(x.index) #站點列表
    fg=folium.FeatureGroup(name='聚合{}'.format(day)) #圖層名稱
    fg_2=folium.FeatureGroup(name='點資料{}'.format(day), show=False)#圖層名稱
    fg_3=folium.FeatureGroup(name='熱力圖', show=False)#圖層名稱
    marker_cluster=MarkerCluster().add_to(fg) #聚合點設定
    Heat_data = [[row['lat'], row['lng']] for index, row in x.iterrows()] #將點位資料加入陣列
    def pop(x): #設定讀取圖片
        encoded = base64.b64encode(open(x, 'rb').read()).decode()
        html = '<img src="data:image/jpeg;base64,{}">'.format
        iframe = folium.IFrame(html(encoded), width=650, height=540)
        popup = folium.Popup(iframe, max_width=2650)
        return popup
    for i in bikedata: #迭代站點
        try:
            m1 = folium.Marker(location=[x.at[i,'lat'],x.at[i,'lng']],popup=pop(x.at[i,'路徑'])) #將點加入popup
            m1.add_to(marker_cluster)
            fg_2.add_child(folium.Marker(location=[x.at[i,'lat'],x.at[i,'lng']],popup=pop(x.at[i,'路徑'])))
        except FileNotFoundError :
            print('notfound')
            m1 = folium.Marker(location=[x.at[i,'lat'],x.at[i,'lng']],popup=i)
            m1.add_to(marker_cluster)
            fg_2.add_child(folium.Marker(location=[x.at[i,'lat'],x.at[i,'lng']],popup=i))
    HeatMap(Heat_data).add_to(fg_3)
    m.add_child(fg)
    m.add_child(fg_2)
    m.add_child(fg_3) #將熱力圖、點位資料、聚合點位資料繪製入地圖
    m.add_child(folium.LayerControl()) #增加圖層控制項
    m.save("{}.html".format(day)) #儲存成html
def main(day):
    data_iterater(day)
    draw(day)
    timetoloc(day)
    fo(day)
print('now lets start these work!')
while True :
    current_datetime = datetime.datetime.now() #獲取時間
    b=current_datetime.strftime('%H%M') 
    if b=='0000' : #00:00開始程式
        print('start :)')
        while True :
            flag=True #布林指示物
            k=0 #計數器
            current_datetime = datetime.datetime.now() #獲取時間
            p=current_datetime.strftime('%m-%d') #字串整理
            if not os.path.isdir(p): os.mkdir(p) #如果目錄中沒有對應的資料夾，建立資料夾
            while True :
                try :
                    while flag:
                        Youbike_url = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'
                        #Youbike資料
                        r = requests.get(Youbike_url)
                        #抓取
                        data = r.json()
                        x_df = json_normalize(data)
                        #JsonToDf
                        current_datetime = datetime.datetime.now()
                        save_file_name = '{y}/{x}_data.csv'.format(y=p,x=current_datetime.strftime('%Y-%m-%d_%H-%M-%S'))
                        x_df.to_csv(save_file_name, encoding='utf-8', index=False)
                        #以時間為名儲存檔案
                        print(k) #顯示進度
                        time.sleep(59) #等待一分鐘
                        k+=1 #計數加1
                        midnight=current_datetime.strftime('%H%M') #獲取時間
                        if k>10 and midnight<= '0005' : #午夜判定句
                            flag=False #終止迴圈
                            day=current_datetime.strftime('%m-%d'-1) #獲取日期
                            main('{}-{}'.format(day[:2],str(int(day[-2:])-1))) #主程式
                            print('wow i done a day of work !!!') #結束訊息
                except :
                    print("Connection refused by the server..")
                    print("Let me sleep for 60 seconds")
                    print("ZZzzzz...")
                    time.sleep(60)
                    print("Was a nice sleep, now let me continue...")
                    continue
                break