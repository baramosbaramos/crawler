import pickle
import MySQLdb 
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.linear_model import Lasso
import os
from dotenv import load_dotenv

from st_list import st_list


def machine_learning(station_name, station_code):

    station_list = st_list

    load_dotenv()

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor() 

    # for station_name, station_code in station_list:
    # trainingData（学習データ）にアクセス
    x = []
    y = []
    c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')  
    for row in c.fetchall(): 
        index, property_name, construction_age, total_fee, floor_space, access_time, url, room_type, shikikin_reikin, bill_type = row

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
        

    # 学習
    # train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, random_state=42)
    
    clf = Lasso(alpha=1.5)
    clf.fit(x, y)
    print(index, '件のデータを学習しました')

    

    #学習結果DBを作成する。
    with open(f'./learning_model/suumo_{station_code}.pkl', 'wb') as fp:
        pickle.dump(clf, fp)

    conn.close()