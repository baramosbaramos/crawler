from lib2to3.pgen2.token import OP
from traceback import print_tb
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exc

import datetime
import time
import MySQLdb 

import os
from dotenv import load_dotenv
import re

from st_list import st_list

def crawling(crawling_page=50):

    start_time = time.time()
    load_dotenv()

    def driver_operation():
        options = Options()
        options.add_argument('--headless')
        # driver_path = '/Users/sou/Desktop/React/Tutorial/py_crawler/driver/chromedriver'
        driver_path = '/Users/sou/Desktop/py_crawler/suumo_crawler/driver/chromedriver'
        driver = webdriver.Chrome(driver_path, options=options)

        return driver


    # driverリクエスト
    driver = driver_operation()
    station_list = st_list
    # area_code = os.environ['STATION_CODE']
    # station_name = os.environ['STATION_NAME']
    

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor() 

    # station_listのクローリング
    for station_name, station_code in station_list:
        
        print(station_name + "駅クローリング中")
        # 初回リクエスト
        driver.get(f'https://suumo.jp/chintai/tokyo/{station_code}/')

        c.execute(f'DROP TABLE IF EXISTS `{station_code}_properties_trainingData`')
        c.execute(f"""
            CREATE TABLE `{station_code}_properties_trainingData` (
                `index` integer,
                `property_name` text,
                `construction_age` integer,
                `total_fee` integer,
                `floor_space` float,
                `access_time` integer,
                `url` text
            )
        """)

        page = 0
        index = 1
        while True:
            page += 1
            sleep(1)
            
            # 建物情報のdivタグ取得
            for property_div in driver.find_elements(By.CLASS_NAME,"cassetteitem"):
                property_name = property_div.find_element(By.CLASS_NAME, "cassetteitem_content-title").text
               

                access_time = 1000
                for access_div in property_div.find_elements(By.CLASS_NAME, "cassetteitem_detail-text"):
                    if station_name in access_div.text:
                        try:
                            access_time_text = access_div.text
                            if "バス" in access_time_text:
                                access_bus_time = re.findall('バス(.*)分', access_time_text)
                                access_time = int(access_bus_time)*3
                            else:
                                access_time = re.findall('歩(.*)分', access_time_text)
                        except:
                            access_time = 1000
                if access_time == 1000:
                    break

                construction_age_str = property_div.find_element(By.CLASS_NAME, "cassetteitem_detail-col3").find_element(By.TAG_NAME, "div").text
                if construction_age_str == '新築':
                    construction_age = 0
                else:
                    construction_age = int(construction_age_str.strip("築年"))
                
                # 部屋情報のtrタグ取得
                for individual_property_tr in property_div.find_elements(By.CLASS_NAME, "js-cassette_link"):
                    try:
                        # property_info_list = []
                        
                        rent = int(float(individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_other-emphasis.ui-text--bold").text.replace('万円', '')) * 10000)
                        
                        management_fee_str = individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_price.cassetteitem_price--administration").text
                        if '円' in management_fee_str:
                            management_fee = int(management_fee_str.replace('円', ''))
                        else:
                            management_fee = 0
                        total_fee = rent + management_fee

                        floor_space_str = individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_menseki").text
                        floor_space = float(floor_space_str.replace('m2', ''))

                        url = individual_property_tr.find_element(By.CLASS_NAME, "js-cassette_link_href.cassetteitem_other-linktext").get_attribute('href')
                        
                        # property_info_list += [index, property_name, construction_age, total_fee, floor_space]

                        c.execute(f'INSERT INTO `{station_code}_properties_trainingData` VALUES (%s, %s, %s, %s, %s, %s, %s)', (index, property_name, construction_age, total_fee, floor_space, access_time, url))

                        index += 1
                        # print(index)
                    except Exception:
                        break
                                        
            print(page)

            # 次ページの読み込み    
            try:
                next_link_a = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
                next_link_text = next_link_a.text
                
                # print(next_link_text)
                driver.get(next_link_a.get_attribute('href'))
                if page > crawling_page:
                    break
            except exc.NoSuchElementException:
                break

    # MySQLクローズ
    conn.commit()  
    # c.execute(f'SELECT * FROM `{station_code}_properties_trainingData`')  
    # for row in c.fetchall(): 
    #     print(row)  
    conn.close()

    driver.close()
    finish_time = time.time()
    print('経過時間', finish_time-start_time)