from calendar import different_locale
from copyreg import pickle
import MySQLdb 
import os
from dotenv import load_dotenv
import numpy as np
import pickle
from sklearn.metrics import accuracy_score

from st_list import st_list


def predicting_rent(station_name, station_code):

    station_list = st_list

    load_dotenv()

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor() 

    # for station_name, station_code in station_list:

    
    # 学習結果データ呼び出し
    with open(f'./learning_model/suumo_{station_code}.pkl', 'rb') as fp:
        clf = pickle.load(fp)

    # 学習データDBにアクセス
    x = []
    y = []
    c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')  

    # 文字データを数値データに置き換えた上で、賃料予測を実施する。
    for row in c.fetchall(): 
        index, property_name, construction_age, total_fee, floor_space, access_time, url, room_type,shikikin_reikin, bill_type = row

        if room_type=="1K":
            room_type = 1
        elif room_type=="1DK":
            room_type = 2
        elif room_type=="1LDK":
            room_type = 3
        elif room_type=="1R":
            room_type = 4
        elif room_type=="2LDK":
            room_type = 5
        elif room_type=="3LDK":
            room_type = 6
        elif room_type=="1SLDK":
            room_type = 7
        elif room_type=="2SLDK":
            room_type = 8
        elif room_type=="3SLDK":
            room_type = 9
        else:
            room_type = 10
        
        if bill_type=="アパート":
            bill_type = 1
        elif bill_type=="マンション":
            bill_type = 2
        else:
            bill_type = 10

        y.append(total_fee)
        x.append(np.array([construction_age, access_time, floor_space, room_type, shikikin_reikin, bill_type]))

    # 賃料判定
    projected_rent_list = clf.predict(x)

    # 予測賃料テーブル作成　→ 最終データであり、これをHTMLに表示する。
    c.execute(f'DROP TABLE IF EXISTS `{station_code}_properties`')
    c.execute(f"""
        CREATE TABLE `{station_code}_properties` (
            `index` integer,
            `property_name` text,
            `construction_age` integer,
            `total_fee` integer,
            `floor_space` float,
            `access_time` integer,
            `projected_rent` integer,
            `difference` integer,
            `deviation_rate` float,
            `url` text,
            `room_type` text,
            `shikikin_reikin` float,
            `bill_type` text
        )
    """)

    # 予測した賃料データをプラスして保存
    i = 0
    c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')
    for row in c.fetchall(): 
        index, property_name, construction_age, total_fee, floor_space, access_time, url, room_type,shikikin_reikin, bill_type  = row
        projected_rent = int(projected_rent_list[i])
        # 両方マイナスが良い
        difference = total_fee - projected_rent
        deviation_rate = difference / projected_rent
        # DBにinsert
        sql = f'INSERT INTO `{station_code}_properties` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        data_tuple = (index, property_name, construction_age, total_fee, floor_space, access_time, projected_rent, difference, deviation_rate, url, room_type, shikikin_reikin, bill_type)
        c.execute(sql, data_tuple)

        i += 1
            
    conn.commit()  
    conn.close()

    print(station_name + "駅予測終了")