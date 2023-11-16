from lib2to3.pgen2.token import OP
from traceback import print_tb
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exc

import csv
import datetime
import time

start_time = time.time()

def csv_operation():
    csv_date = datetime.datetime.today().strftime("%Y%m%d")
    csv_file_name = 'google_python_' + csv_date + '.csv'
    f = open('./suumo_db/' + csv_file_name, 'w', encoding='cp932', errors='ignore')
    
    # csv_header = ["検索順位", "URL", "サマリー"]
    # writer.writerow(csv_header)

    return f

def driver_operation():
    options = Options()
    options.add_argument('--headless')
    driver_path = '/Users/sou/Desktop/React/Tutorial/py_crawler/driver/chromedriver'
    driver = webdriver.Chrome(driver_path, options=options)

    return driver

# driverリクエスト
driver = driver_operation()
area_code = 'ek_01820'
driver.get(f'https://suumo.jp/chintai/tokyo/{area_code}/')

# CSV操作
f = csv_operation()
writer = csv.writer(f, lineterminator='\n')
csv_date = datetime.datetime.today().strftime("%Y%m%d")
csv_file_name = 'google_python_' + csv_date + '_' + area_code + '.csv'

page = 0
with open('./suumo_property_info_db/' + csv_file_name, 'w') as h:
    while True:
        page += 1
        index = 1
        sleep(1)

        # 建物情報のdivタグ取得
        for property_div in driver.find_elements(By.CLASS_NAME,"cassetteitem"):
            property_name = property_div.find_element(By.CLASS_NAME, "cassetteitem_content-title").text
            # print(property_name)

            for access_div in property_div.find_elements(By.CLASS_NAME, "cassetteitem_detail-text"):
                if '飯田橋' in access_div.text:
                    access_time = access_div.text

            construction_age_str = property_div.find_element(By.CLASS_NAME, "cassetteitem_detail-col3").find_element(By.TAG_NAME, "div").text
            if construction_age_str == '新築':
                construction_age = 0
            else:
                construction_age = int(construction_age_str.strip("築年"))
            
            # 部屋情報のtrタグ取得
            for individual_property_tr in property_div.find_elements(By.CLASS_NAME, "js-cassette_link"):
                property_info_list = []
                
                rent = float(individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_other-emphasis.ui-text--bold").text.replace('万円', '')) * 10000
                
                management_fee_str = individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_price.cassetteitem_price--administration").text
                if '円' in management_fee_str:
                    management_fee = float(management_fee_str.replace('円', ''))
                else:
                    management_fee = 0
                total_fee = rent + management_fee

                floor_space_str = individual_property_tr.find_element(By.CLASS_NAME, "cassetteitem_menseki").text
                floor_space = float(floor_space_str.replace('m2', ''))
                
                property_info_list += [index, property_name, construction_age, total_fee, floor_space]

                # CSV書き込み
                writer = csv.writer(h)
                writer.writerow(property_info_list)
                # print(index)
                index += 1     
                                  

        # 次ページの読み込み    
        try:
            next_link_a = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
            next_link_text = next_link_a.text
            print(page, "ページ目")
            # print(next_link_text)
            driver.get(next_link_a.get_attribute('href'))
            if page > 2:
                break
        except exc.NoSuchElementException:
            break

h.close()

driver.close()
finish_time = time.time()
print('経過時間', finish_time-start_time)

