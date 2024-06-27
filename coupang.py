from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

import chromedriver_autoinstaller
import os

from bs4 import BeautifulSoup
import time
import logConfig

# Find the button for title
def product_titles_present(driver):
  product_titles = driver.find_elements(By.CLASS_NAME, 'search-product')
  filtered_titles = [title for title in product_titles if 'search-product__ad-badge' not in title.get_attribute('class')]
  return filtered_titles
# Find the button to click
def delivery_guide_button_present(driver):
  print("try find")
  return driver.find_element(By.XPATH, "//div[@id='btfTab']//ul[@class='tab-titles']//li[@name='etc']")

# Find the table that contains target information
def seller_table_present(driver):
  return driver.find_element(By.XPATH, "//div[@class='product-item__table product-seller']//table[@class='prod-delivery-return-policy-table']")

def scrape_coupang(keyword, page):
  logConfig.logger.info(f'{keyword} 키워드로 쿠팡 스토어 크롤링 시작')
  logConfig.logger.info(f'총 {page} 페이지 검색')

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

  # Use WebDriverWait to wait for product titles to be present
  wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed

  link_list = []
  seller_phone_number = []
  seller_email = []

  def scrape_list_page(page):
    # URL to scrape
    url = f"https://www.coupang.com/np/search?component=&q={keyword}&channel=user&page={page}"
    print(f'url: {url}')
    # Navigate to the URL
    driver.get(url)

    # Wait for the product titles to be present on the page
    product_titles = wait.until(product_titles_present)

    # Loop through the product titles and find anchor tags
    for title in product_titles:
      anchorTag = title.find_element(By.TAG_NAME, 'a')
      link_list.append(anchorTag.get_attribute('href'))

  for current_page in range(page):
    scrape_list_page(current_page + 1)
    logConfig.logger.info(f'{current_page + 1}/{page} 페이지 완료')

  print(link_list)
  logConfig.logger.info(f'총 {len(link_list)}개의 상품 검색 완료. 판매자 데이터 스크래핑 시작.')

  for idx, target_url in enumerate(link_list):
    print(target_url)
    driver.get(target_url)
    time.sleep(1.5)
    # Click '배송/교환/반품 안내' button
    delivery_guide_button = None

    try :
      delivery_guide_button = wait.until(delivery_guide_button_present)
    except :
      print("exception")
      continue

    if delivery_guide_button is None:
      seller_phone_number.append('-')
      seller_email.append('-')
      continue

    delivery_guide_button.click()

    seller_table = wait.until(seller_table_present)
    
    table_html_content = seller_table.get_attribute('innerHTML')
    soup = BeautifulSoup(table_html_content, 'html.parser')
    tbody = soup.find('tbody')

    # print(tbody)
    if tbody:
      tr_list = tbody.find_all('tr')
      if len(tr_list) == 1:
        seller_phone_number.append('-')
        seller_email.append('-')
      elif len(tr_list) == 4:
        print(f'tr len is 4, {tr_list[1].find_all("td")[0].text}, {tr_list[1].find_all("td")[1].text}')
        print(f'tr len is 4, {tr_list[2].find_all("td")[0].text}, {tr_list[2].find_all("td")[1].text}')
        seller_phone_number.append(tr_list[1].find_all('td')[0].text)
        seller_email.append(tr_list[1].find_all('td')[1].text)
      elif len(tr_list) == 5:
        print(f'tr len is 5, {tr_list[1].find_all("td")[0].text}, {tr_list[1].find_all("td")[1].text}')
        print(f'tr len is 5, {tr_list[2].find_all("td")[0].text}, {tr_list[2].find_all("td")[1].text}')
        seller_phone_number.append(tr_list[2].find_all('td')[0].text)
        seller_email.append(tr_list[2].find_all('td')[1].text)
    else:
      seller_phone_number.append('-')
      seller_email.append('-')
      print('no tbody')
    logConfig.logger.info(f'{idx + 1}번째 상품 완료')
    print(f'{idx + 1}번째 상품 완료')

  # Close the WebDriver when done
  driver.quit()

  result = {}
  result['링크'] = link_list
  result['연락처'] = seller_phone_number
  result['e-mail'] = seller_email

  return result