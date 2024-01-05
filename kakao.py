from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import requests
from urllib.parse import urlparse
import pandas as pd
import os

import logConfig

def product_titles_present(driver):
  product_titles = driver.find_elements(By.CLASS_NAME, 'link_product')
  return product_titles

def paging_num_present(driver): 
  return driver.find_elements(By.XPATH, "//div[@class='paging_num']/*[@class='link_paging']")
def link_arrow_present(driver): 
  return driver.find_element(By.XPATH, "//button[@class='link_arrow'][2]")


def scrape_kakao_store(keyword, page):
  download_path = "./result_kakao"

  # Windowless mode feature (Chrome) and chrome message handling.
  options = webdriver.ChromeOptions()
  options.headless = True # Runs driver without opening a chrome browser.
  options.add_experimental_option("excludeSwitches", ["enable-logging"])

  # Initialization of web driver
  driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = options)
  driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                          {"source": """ Object.defineProperty(navigator, 'webdriver', {get: () => undefined }) """ }
                        )

  # Use WebDriverWait to wait for product titles to be present
  wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed

  # URL to scrape
  url = f"https://store.kakao.com/search/result/product?q={keyword}"
  # Navigate to the URL
  driver.get(url)

  time.sleep(3)

  def goto_target_page(page):
    paging_num = wait.until(paging_num_present)
    link_arrow_next = wait.until(link_arrow_present)
    # if page is 1, we don't need to do anything
    if page == 1: 
      return
    print(page)
    if page % 5 != 1:
      # print(paging_num[page % 5].get_attribute['outerHTML'])
      paging_num[page % 5 - 1].click()
    else:
      link_arrow_next.click()

  seller_list = []

  for i in range(page):
    goto_target_page(i + 1)
    time.sleep(2)

    # Wait for the product titles to be present on the page
    product_titles = wait.until(product_titles_present)

    for i, anchor in enumerate(product_titles):
      # print(anchor.get_attribute('href'))
      url = urlparse(anchor.get_attribute('href'))
      seller_name = url.path.split('/')[1]
      seller_list.append(seller_name)

    logConfig.logger.info(f'{i + 1}번째 페이지 완료')
    

  result = {
    'profileImageUrl': [],
    'name': [],
    'introduce': [],
    'phoneNumber': [],
    'corporateName': [],
    'presidentName': [],
    'businessRegistrationNumber': [],
    'onlineOrderRegistrationNumber': [],
    'addressPost': [],
    'domain': [],
    'mainEmail': [],
    'isFarmer': [],
    'consultId': [],
  }
  # get each seller's data after getting seller list
  for idx, seller in enumerate(seller_list):
    # Send https get request to api and get data of sellers
    seller_url = f'https://store.kakao.com/a/brandstore/{seller}/profile'
    response = requests.get(seller_url)
    if response.status_code == 200:
      json_data = response.json()
      print(json_data)
      result['profileImageUrl'].append(json_data['data'].get('profileImageUrl', ''))
      result['name'].append(json_data['data']['store'].get('name', ''))
      result['introduce'].append(json_data['data']['store'].get('introduce', ''))
      result['phoneNumber'].append(json_data['data']['store'].get('phoneNumber', ''))
      result['corporateName'].append(json_data['data']['store'].get('corporateName', ''))
      result['presidentName'].append(json_data['data']['store'].get('presidentName', ''))
      result['businessRegistrationNumber'].append(json_data['data']['store'].get('businessRegistrationNumber', ''))
      result['onlineOrderRegistrationNumber'].append(json_data['data']['store'].get('onlineOrderRegistrationNumber', ''))
      result['addressPost'].append(json_data['data']['store'].get('addressPost', ''))
      result['domain'].append(json_data['data']['store'].get('domain', ''))
      result['mainEmail'].append(json_data['data']['store'].get('mainEmail', ''))
      result['isFarmer'].append(json_data['data']['store'].get('isFarmer', ''))
      result['consultId'].append(json_data['data']['store'].get('consultId', ''))

    logConfig.logger.info(f'{idx + 1}번째 상품 완료')

  def save_seller_dataframe():
    # Saves dataframe in excel file format.
    print("Storing data, almost done....")
    reviews_ratings_df = pd.DataFrame(result)
    time.sleep(2)
    # Convert to CSV and save in Downloads.
    if not os.path.exists(download_path):
      os.makedirs(download_path)

    reviews_ratings_df.to_excel(f'{download_path}/{keyword}.xlsx', index=False)
    data_rows = "{:,}".format(reviews_ratings_df.shape[0])

  save_seller_dataframe()
  print(seller_list)
  print(len(seller_list))
  logConfig.logger.info(f'엑셀로 변환 완료')

  driver.quit()