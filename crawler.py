from lib2to3.pgen2.token import OP
from traceback import print_tb
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exc
from selenium.common.exceptions import TimeoutException

import datetime
import time
import MySQLdb 

import os
from dotenv import load_dotenv
import re

from st_list import st_list

def crawling(station_name, station_code, crawling_page=50):

    start_time = time.time()
    load_dotenv()

    def driver_operation():
        options = Options()
        options.add_argument('--headless')
        # driver_path = '/Users/sou/Desktop/React/Tutorial/py_crawler/driver/chromedriver/chromedriver'
        driver_path = '/home/ubuntu/crawler/crawler/driver/chromedriver'
        driver = webdriver.Chrome(options=options)

        return driver


    # driverリクエスト
    driver = driver_operation()
    # station_list = st_list
    # area_code = os.environ['STATION_CODE']
    # station_name = os.environ['STATION_NAME']
    

    # MySQL接続
    conn = MySQLdb.connect(db='py_scraping', user='scraper', passwd=os.environ['PASS'], charset='utf8mb4')
    c = conn.cursor() 

    # station_listのクローリング
    # for station_name, station_code in station_list:
    
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
            `url` text,
            `room_type` text,
            `shikikin_reikin` float,
            `bill_type` text
        )
    """)

    page = 0
    index = 1
    while True:
        page += 1
        # print(str(page) + "ページ")
        sleep(0.2)
        error_count = 0
        # 建物情報のdivタグを全て取得してループ
        try:
            for property_div in driver.find_elements(By.CLASS_NAME,"cassetteitem"):

                #徒歩何分の取得
                #access_timeの初期値を1000とし、更新されなければスキップする。
                access_time = 1000
                for access_div in property_div.find_elements(By.CLASS_NAME, "cassetteitem_detail-text"):
                    try:
                        s_name = re.findall('/(.*)駅', access_div.text)[0]
                        if station_name == s_name:
                            access_time_text = access_div.text
                            if "バス" in access_time_text:
                                access_bus_time = re.findall('バス(.*)分', access_time_text)
                                access_time = int(access_bus_time)*3
                            else:
                                access_time = re.findall('歩(.*)分', access_time_text)
                    except:
                        pass
                if access_time == 1000:
                    continue
                
                #物件名の取得
                property_name = property_div.find_element(By.CLASS_NAME, "cassetteitem_content-title").text
                # print(property_name)
              

                # 建物タイプの取得
                bill_type = property_div.find_element(By.CLASS_NAME, "ui-pct.ui-pct--util1").text
                if "賃貸" in bill_type:
                    bill_type = bill_type.replace("賃貸", "")

                 # 築年数の取得
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
                        room_type = individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_madori").text
                        if room_type == "ワンルーム":
                            room_type = room_type.replace("ワンルーム", "1R")
                        
                        # kai_str = individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_madori").text
                        # if '階' in management_fee_str:
                        #     kai = int(kai_str.replace('階', ''))
                        # else:
                        #     kai = 0
                        shikikin_str= individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_price.cassetteitem_price--deposit").text
                        if '万円' in shikikin_str:
                            shikikin = float(shikikin_str.replace('万円', ''))
                        else:
                            shikikin = 0
                        reikin_str= individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_price.cassetteitem_price--gratuity").text
                        if '万円' in reikin_str:
                            reikin = float(reikin_str.replace('万円', ''))
                        else:
                            reikin = 0
                        shikikin_reikin = shikikin + reikin

                        # print(index, property_name, construction_age, total_fee, floor_space, access_time, url,room_type,shikikin_reikin, bill_type)
                        
                        c.execute(f'INSERT INTO `{station_code}_properties_trainingData` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (index, property_name, construction_age, total_fee, floor_space, access_time, url,room_type,shikikin_reikin, bill_type))
                        index += 1
                        # print(index)
                    except Exception as e:
                        print(e)

        except TimeoutException as e:
            print(e)
            error_count += 1
            if error_count >= 2:
                print("エラーカウントが２回を超えたためブレイクしました。物件を取得できません。")
                break
        except Exception as e:
            print("タグがありません。")
            print(e)


        # 次ページの読み込み    
        try:
            next_link_a = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
            next_link_text = next_link_a.text
            
            driver.get(next_link_a.get_attribute('href'))
            if page > crawling_page:
                break
        except exc.NoSuchElementException:
            break
        except TimeoutException as e:
            print(e)
            error_count += 1
            if error_count >= 2:
                print("２回タイムアウトしました。")
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