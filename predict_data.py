from calendar import different_locale
from copyreg import pickle
import MySQLdb 
import os
from dotenv import load_dotenv
import numpy as np
import pickle
from sklearn.metrics import accuracy_score

from st_list import st_list


def predicting_rent():

    station_list = st_list

    load_dotenv()
    area_code = os.environ['STATION_CODE']

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor() 

    for station_name, station_code in station_list:

        print(station_name + "駅予測開始")
        # 学習データ呼び出し
        with open(f'./learning_model/suumo_{station_code}.pkl', 'rb') as fp:
            clf = pickle.load(fp)

        # 物件DBにアクセス
        x = []
        y = []
        c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')  
        for row in c.fetchall(): 
            index, property_name, construction_age, total_fee, floor_space, access_time, url = row
            y.append(total_fee)
            x.append(np.array([construction_age, access_time, floor_space]))

        # 賃料判定
        projected_rent_list = clf.predict(x)

        # 予測賃料テーブル作成
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
                `url` text
            )
        """)

        # 予測賃料データ保存
        i = 0
        c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')
        for row in c.fetchall(): 
            index, property_name, construction_age, total_fee, floor_space, access_time, url = row
            projected_rent = int(projected_rent_list[i])
            # 両方マイナスが良い
            difference = total_fee - projected_rent
            deviation_rate = difference / projected_rent
            # DBにinsert
            sql = f'INSERT INTO `{station_code}_properties` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            data_tuple = (index, property_name, construction_age, total_fee, floor_space, access_time, projected_rent, difference, deviation_rate, url)
            c.execute(sql, data_tuple)

            i += 1
            
    conn.commit()  
    conn.close()