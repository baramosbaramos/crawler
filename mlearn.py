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


def machine_learning():

    station_list = st_list

    load_dotenv()
    # area_code = os.environ['STATION_CODE']

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor() 

    for station_name, station_code in station_list:
        # 学習用DBにアクセス
        x = []
        y = []
        c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')  
        for row in c.fetchall(): 
            index, property_name, construction_age, total_fee, floor_space, access_time, url = row
            y.append(total_fee)
            x.append(np.array([construction_age, access_time, floor_space]))

        # 学習
        # train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, random_state=42)
        clf = Lasso(alpha=1.5)
        clf.fit(x, y)
        print(index, '件のデータを学習しました')

        with open(f'./learning_model/suumo_{station_code}.pkl', 'wb') as fp:
            pickle.dump(clf, fp)

    conn.close()