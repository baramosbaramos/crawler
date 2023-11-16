from lib2to3.pgen2.token import OP
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

# CSV操作
f = csv_operation()
writer = csv.writer(f, lineterminator='\n')
driver = driver_operation()

# area_code = 'ek_19670'
area_code = 'ek_01820'
# sam_url = 'https://suumo.jp/chintai/tokyo/ek_19670/?page=329&rn=0005'
driver.get(f'https://suumo.jp/chintai/tokyo/{area_code}/')
# driver.get(sam_url)

# 検索操作
# search_bar = driver.find_element_by_class_name('cassetteitem_content-title')
# search_bar.send_keys('python')
# search_bar.submit()

i = 0
# item = 1

while True:
    i = i + 1
    sleep(1)
    for property_link_a in driver.find_elements(By.CLASS_NAME,"js-cassette_link_href.cassetteitem_other-linktext"):
        property_link_list = []
        property_link = property_link_a.get_attribute('href')
        property_link_list.append(property_link)
        writer.writerow(property_link_list)
        # item = item + 1
    
    try:
        next_link_a = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
        next_link_text = next_link_a.text
        print(i, "ページ目")
        print(next_link_text)
        driver.get(next_link_a.get_attribute('href'))

        if i > 0:
            break
    except exc.NoSuchElementException:
        break

f.close()

csv_date = datetime.datetime.today().strftime("%Y%m%d")
csv_file_name = 'google_python_' + csv_date + '.csv'
with open('./suumo_property_info_db/' + csv_file_name, 'w') as h:
    with open('./suumo_db/' + csv_file_name, encoding='utf8', newline='') as g:
        csvreader = csv.reader(g)
        index = 1
        for row in csvreader:
            
            property_info_list = []
            driver.get(row[0])

            property_name_h1 = driver.find_element(By.CLASS_NAME, "section_h1-header-title")
            property_name = property_name_h1.text
            property_info_list.append(property_name)

            access_time_div = driver.find_element(By.CLASS_NAME, "property_view_table-read")
            access_time = access_time_div.text
            property_info_list.append(access_time)
            
            writer = csv.writer(h)
            writer.writerow(property_info_list)
            sleep(1)
            print(index, property_name)

            index += 1


           
        


driver.close()
finish_time = time.time()
print('経過時間', finish_time-start_time)
    
    # next_link = driver.find_element_by_id('pnnext')
    # driver.get(next_link.get_attribute('href'))
    # if i > 10:
    #     break

