import requests
import pandas as pd

import time
import os

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

def scrape_ohouse(keyword, page):

  product_id_list = []

  for i in range(page):
    url = f"https://ohou.se/productions/feed.json?v=7&query={keyword}&search_affect_type=Typing&page={page}&per=20"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
      json_data = response.json()
      for product in json_data['productions']:
        print(f"{i}: {product['name']}")
        product_id_list.append(product['id'])
    else:
      print(response.status_code)

  seller_info_company = []
  seller_info_representative = []
  seller_info_cs_phone = []
  seller_info_address = []
  seller_info_email = []
  seller_info_license = []

  for product_id in product_id_list:
    url = f"https://ohou.se/productions/{product_id}/delivery.json"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
      json_data = response.json()
      seller_info = json_data['seller_info']
      seller_info_company.append(seller_info.get('company', ''))
      seller_info_representative.append(seller_info.get('representative', ''))
      seller_info_cs_phone.append(seller_info.get('cs_phone', ''))
      seller_info_address.append(seller_info.get('address', ''))
      seller_info_email.append(seller_info.get('email', ''))
      seller_info_license.append(seller_info.get('license', ''))

    else:
      print(response.status_code)
    
  return {
    'seller_info_company': seller_info_company,
    'seller_info_representative': seller_info_representative,
    'seller_info_cs_phone': seller_info_cs_phone,
    'seller_info_address': seller_info_address,
    'seller_info_email': seller_info_email,
    'seller_info_license': seller_info_license,
  }

keyword = '의자'
download_path = "./result_ohouse"

result =  scrape_ohouse(keyword, 1)

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