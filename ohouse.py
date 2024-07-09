import requests
import logConfig
import time
import random
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

import chromedriver_autoinstaller
import os

import time
import logConfig


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def scrape_ohouse(keyword, page):
  chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
  driver_path = f'./chromedriver/{chrome_ver}/chromedriver.exe'

  if os.path.exists(driver_path):
    print(f"chrom driver is installed: {driver_path}")
  else:
    if not os.path.exists(f'./chromedriver'):
      os.makedirs(f'./chromedriver')
    print(f"install the chrome driver(ver: {chrome_ver})")
    chromedriver_autoinstaller.install(path=f'./chromedriver')

  # Windowless mode feature (Chrome) and chrome message handling.
  options = webdriver.ChromeOptions()
  options.headless = True # Runs driver without opening a chrome browser.
  options.add_experimental_option("excludeSwitches", ["enable-logging"])

  # Initialization of web driver
  driver = webdriver.Chrome(service=ChromeService(executable_path=driver_path), options = options)
  driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                          {"source": """ Object.defineProperty(navigator, 'webdriver', {get: () => undefined }) """ }
                        )

  def find_json(driver):
    print("try find")
    return driver.find_element(By.XPATH, "(//pre)[1]")

  # Use WebDriverWait to wait for product titles to be present
  wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed


  logConfig.logger.info(f'{keyword} 키워드로 오늘의 집 크롤링 시작')
  product_id_list = []

  for i in range(page):
    try:
      time.sleep(random.random() * 5 + 3)

      url = f"https://ohou.se/productions/feed.json?v=7&query={keyword}&search_affect_type=Typing&page={page}&per=20"

      # Navigate to the URL
      driver.get(url)

      # Wait for the product titles to be present on the page
      product_titles = wait.until(find_json)

      json_data = json.loads(product_titles.text)

      for product in json_data['productions']:
        print(f"{i}: {product['name']}")
        product_id_list.append(product['id'])

      logConfig.logger.info(f'{i + 1}/{page} 페이지 완료')
    
    except TimeoutException as e:
      logConfig.logger.error(f'페이지 로드 시간 초과: {url}')
    
    except json.JSONDecodeError:
      logConfig.logger.error(f'JSON 디코드 에러: {product_titles.text}')
    
    except Exception as e:
      logConfig.logger.error(f'예기치 않은 에러 발생: {str(e)}')
  
  logConfig.logger.info(f'총 {len(product_id_list)}개의 상품 검색 완료. 판매자 데이터 스크래핑 시작.')

  seller_info_company = []
  seller_info_representative = []
  seller_info_cs_phone = []
  seller_info_address = []
  seller_info_email = []
  seller_info_license = []

  print(product_id_list)

  for idx, product_id in enumerate(product_id_list):
    try:
      time.sleep(random.random() * 5 + 3)
      url = f"https://ohou.se/productions/{product_id}/delivery.json"
      print(url)

      # Navigate to the URL
      driver.get(url)

      # Wait for the product titles to be present on the page
      product_titles = wait.until(find_json)

      print(type(product_titles))

      print(product_titles.text)
      json_data = json.loads(product_titles.text)

      seller_info = json_data['seller_info']
      seller_info_company.append(seller_info.get('company', ''))
      seller_info_representative.append(seller_info.get('representative', ''))
      seller_info_cs_phone.append(seller_info.get('cs_phone', ''))
      seller_info_address.append(seller_info.get('address', ''))
      seller_info_email.append(seller_info.get('email', ''))
      seller_info_license.append(seller_info.get('license', ''))

      print(json_data)

      logConfig.logger.info(f'{idx + 1}번째 상품 완료')

    except TimeoutException as e:
      logConfig.logger.error(f'페이지 로드 시간 초과: {url}')
    
    except json.JSONDecodeError:
      logConfig.logger.error(f'JSON 디코드 에러: {product_titles.text}')
    
    except Exception as e:
      logConfig.logger.error(f'예기치 않은 에러 발생: {str(e)}')
    
  return {
    '상호': seller_info_company,
    '대표자': seller_info_representative,
    '고객센터 전화번호': seller_info_cs_phone,
    '사업장 소재지': seller_info_address,
    'E-mail': seller_info_email,
    '사업자 등록 번호': seller_info_license,
  }