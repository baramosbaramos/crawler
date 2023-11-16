from calendar import different_locale
from copyreg import pickle
import MySQLdb 
import os
from dotenv import load_dotenv
import numpy as np
import pickle
from sklearn.metrics import accuracy_score
import json


def seaching_data(floor_space=0, total_fee=100000000, access_time=20, construction_age=50, diff='difference'):
    load_dotenv()
    area_code = os.environ['STATION_CODE']

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor(MySQLdb.cursors.DictCursor) 
    query = f'SELECT * FROM `{area_code}_properties` where floor_space > {floor_space} and total_fee < {total_fee} and access_time < {access_time} and construction_age < {construction_age} order by {diff}' 

    # 乖離率降順で上位２０件表示
    # c.execute(f'SELECT * FROM `{area_code}_properties` order by deviation_rate')
    c.execute(query)
    # where total_fee < 120000 and access_time < 20 and floor_space > 30 and construction_age < 30 

    search_result_tuple = c.fetchall()
    search_result_json = json.dumps(search_result_tuple, indent=4)
    
    conn.commit()  
    conn.close()

    return search_result_json