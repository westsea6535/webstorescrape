import requests
import logConfig

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def scrape_ohouse(keyword, page):

  logConfig.logger.info(f'{keyword} 키워드로 오늘의 집 크롤링 시작')
  product_id_list = []

  for i in range(page):
    url = f"https://ohou.se/productions/feed.json?v=7&query={keyword}&search_affect_type=Typing&page={page}&per=20"

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
      json_data = response.json()
      for product in json_data['productions']:
        print(f"{i}: {product['name']}")
        product_id_list.append(product['id'])
      logConfig.logger.info(f'{i + 1}/{page} 페이지 완료')
    else:
      print(response.status_code)
      logConfig.logger.info(f'Error while fetching list {idx + 1}. Error code: {response.status_code}')
  
  logConfig.logger.info(f'총 {len(product_id_list)}개의 상품 검색 완료. 판매자 데이터 스크래핑 시작.')

  seller_info_company = []
  seller_info_representative = []
  seller_info_cs_phone = []
  seller_info_address = []
  seller_info_email = []
  seller_info_license = []

  for idx, product_id in enumerate(product_id_list):
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

      logConfig.logger.info(f'{idx + 1}번째 상품 완료')
    else:
      print(response.status_code)
      logConfig.logger.info(f'Error while fetching product {idx + 1}. Error code: {response.status_code}')
    
  return {
    '상호': seller_info_company,
    '대표자': seller_info_representative,
    '고객센터 전화번호': seller_info_cs_phone,
    '사업장 소재지': seller_info_address,
    'E-mail': seller_info_email,
    '사업자 등록 번호': seller_info_license,
  }