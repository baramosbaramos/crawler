from lib2to3.pgen2.token import OP
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import csv
import datetime

def csv_operation():
    csv_date = datetime.datetime.today().strftime("%Y%m%d")
    csv_file_name = 'google_python_' + csv_date + '.csv'
    f = open('./suumo_db/' + csv_file_name, 'w', encoding='cp932', errors='ignore')
    writer = csv.writer(f, lineterminator='\n')
    csv_header = ["検索順位", "URL", "サマリー"]
    writer.writerow(csv_header)

    return f

def driver_operation():
    options = Options()
    options.add_argument('--headless')
    driver_path = '/Users/sou/Desktop/React/Tutorial/py_crawler/driver/chromedriver'
    driver = webdriver.Chrome(driver_path, options=options)

    return driver

# CSV操作
f = csv_operation()

driver = driver_operation()

area_code = 'ek_19670'
driver.get(f'https://suumo.jp/chintai/tokyo/{area_code}/')

# 検索操作
# search_bar = driver.find_element_by_class_name('cassetteitem_content-title')
# search_bar.send_keys('python')
# search_bar.submit()

i = 0
item = 1
while True:
    i = i + 1
    for content_div in driver.find_elements(By.CLASS_NAME,"cassetteitem_content"):
        property_name_div = content_div.find_element(By.CLASS_NAME,"cassetteitem_content-title")
        # elem_a = elem_h3.find_element_by_xpath('..')
        # item = item + 1
        # walking_time = content_div.find_elements(By.CLASS_NAME, "cassetteitem_detail-text").find_element(By.CSS_SELECTOR)
        walking_time_div = content_div.find_elements(By.XPATH, "//div[@class='cassetteitem_detail-text'][@style='font-weight:bold']")
        construction_age_div = content_div.find_element(By.XPATH, "//li[@class='cassetteitem_detail-col3']").find_element(By.TAG_NAME, "div")

        print('-'*30)
        print(property_name_div.text)
        print(walking_time_div[2].text)
        print(construction_age_div.text)
        # csvlist = []
        # csvlist.append(str(item))
        # csvlist.append(elem_h3.text)
        # csvlist.append(elem_a.get_attribute('href'))
        # writer.writerow(csvlist)
        # print(elem_a.get_attribute('href'))
    break
f.close()
driver.close()
    
    # next_link = driver.find_element_by_id('pnnext')
    # driver.get(next_link.get_attribute('href'))
    # if i > 10:
    #     break

