from crawler import crawling 
from mlearn import machine_learning 
from predict_data import predicting_rent
from search_data import seaching_data
import json
import time


start_time = time.time()
# suumoクローリング
crawling(crawling_page=50)

# データ学習
machine_learning()

# 賃料予測
predicting_rent()
finish_time = time.time()
print('経過時間', finish_time-start_time)