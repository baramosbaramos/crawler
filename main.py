from crawler import crawling 
from mlearn import machine_learning 
from predict_data import predicting_rent
from search_data import seaching_data
import json
import time
import datetime
import sys
from st_list import st_list

args = sys.argv
crawling_page = int(args[1])

station_list = st_list

dt_start = datetime.datetime.now()
print(dt_start.strftime('%Y年%m月%d日 %H:%M:%S'))
start_time = time.time()


for station_name, station_code in station_list:
    # suumoクローリング
    crawling(station_name, station_code, crawling_page)

    # データ学習
    machine_learning(station_name, station_code)

    # 賃料予測
    predicting_rent(station_name, station_code)


finish_time = time.time()
print('経過時間', finish_time-start_time)
dt_finish = datetime.datetime.now()
print(dt_finish.strftime('%Y年%m月%d日 %H:%M:%S'))

