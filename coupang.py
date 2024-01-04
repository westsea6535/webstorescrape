from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


from bs4 import BeautifulSoup
import pandas as pd

import time
import os

# Find the button for title
def product_titles_present(driver):
  product_titles = driver.find_elements(By.CLASS_NAME, 'search-product')
  filtered_titles = [title for title in product_titles if 'search-product__ad-badge' not in title.get_attribute('class')]
  return filtered_titles
# Find the button to click
def delivery_guide_button_present(driver):
  try :
    return driver.find_element(By.XPATH, "//div[@id='btfTab']//ul[@class='tab-titles']//li[@name='etc']")
  except NoSuchElementException:
    return None
# Find the table that contains target information
def seller_table_present(driver):
  return driver.find_element(By.XPATH, "//div[@class='product-item__table product-seller']//table[@class='prod-delivery-return-policy-table']")

def scrape_coupang(keyword, page):
  download_path = "./result_coupang"

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

  for page in range(page):
    scrape_list_page(page+1)

  print(link_list)


  result_link = []
  for idx, target_url in enumerate(link_list):
    # if idx <= 13:
      print(target_url)
      driver.get(target_url)
      time.sleep(1.5)
      # Click '배송/교환/반품 안내' button
      delivery_guide_button = wait.until(delivery_guide_button_present)
      if delivery_guide_button is None:
        continue

      delivery_guide_button.click()

      seller_table = wait.until(seller_table_present)
      
      table_html_content = seller_table.get_attribute('innerHTML')
      soup = BeautifulSoup(table_html_content, 'html.parser')
      tbody = soup.find('tbody')

      # print(tbody)
      if tbody:
        tr_list = tbody.find_all('tr')
        if len(tr_list) != 1:
          result_link.append(target_url)
          seller_phone_number.append(tr_list[1].find_all('td')[0].text)
          seller_email.append(tr_list[1].find_all('td')[1].text)
          # print(tr_list[1].find_all('th')[0].text)
          # print(tr_list[1].find_all('td')[0].text)
          # print(tr_list[1].find_all('th')[1].text)
          # print(tr_list[1].find_all('td')[1].text)
      else:
        print('no tbody')
      print('--------------------------')

  # Close the WebDriver when done
  driver.quit()

  result = {}
  result['product_link'] = target_url
  result['seller_phone_number'] = seller_phone_number
  result['seller_email'] = seller_email


  def save_seller_dataframe():
    # Saves dataframe in CSV file format.

    print("Storing data, almost done....")
    reviews_ratings_df = pd.DataFrame(result)
    # reviews_ratings_df = reviews_ratings_df.iloc[1: ,]
    time.sleep(2)
    # Convert to CSV and save in Downloads.
    if not os.path.exists(download_path):
      os.makedirs(download_path)

    # reviews_ratings_df.to_excel(f'{download_path}/result.xlsx', index=False, encoding='utf-8-sig')
    reviews_ratings_df.to_excel(f'{download_path}/{keyword}.xlsx', index=False)
    data_rows = "{:,}".format(reviews_ratings_df.shape[0])

  print(result)
  save_seller_dataframe()