from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QRadioButton, QMessageBox
from PyQt5.QtGui import QIntValidator
from kakao import scrape_kakao_store
from coupang import scrape_coupang
from ohouse import scrape_ohouse

import pandas as pd

import time
import os

class guiForm(QWidget):
  def __init__(self):
    super().__init__()
    self.init_ui()

  def init_ui(self):
    # 위젯 생성
    self.label_platform = QLabel('스토어 선택')
    self.radio_kakao = QRadioButton('카카오스토어')
    self.radio_coupang = QRadioButton('쿠팡')
    self.radio_ohouse = QRadioButton('오늘의 집')

    self.label_keywords = QLabel('검색어:')
    self.input_keywords = QLineEdit()

    self.label_page = QLabel('페이지 개수')
    self.input_page = QLineEdit()
    self.input_page.setValidator(QIntValidator(1, 999))  # 숫자만 입력 가능하도록 설정

    self.button_search = QPushButton('확인')

    # 레이아웃 생성 및 위젯 추가
    layout = QVBoxLayout()
    layout.addWidget(self.label_platform)
    layout.addWidget(self.radio_kakao)
    layout.addWidget(self.radio_coupang)
    layout.addWidget(self.radio_ohouse)

    layout.addWidget(self.label_keywords)
    layout.addWidget(self.input_keywords)

    layout.addWidget(self.label_page)
    layout.addWidget(self.input_page)

    layout.addWidget(self.button_search)

    # 폼에 레이아웃 설정
    self.setLayout(layout)

    # 버튼 클릭 시 이벤트 처리
    self.button_search.clicked.connect(self.onButtonClick)

    # 창 제목 및 크기 설정
    self.setWindowTitle('검색 프로그램')
    self.setGeometry(500, 500, 1000, 300)
    self.setFixedSize(1000, 300)

  def showDialog(self):
      msgBox = QMessageBox()
      msgBox.setIcon(QMessageBox.Information)
      msgBox.setText("작업이 완료되었습니다!")
      msgBox.setWindowTitle("작업 완료")
      msgBox.setStandardButtons(QMessageBox.Ok)
      msgBox.exec_()

  def onButtonClick(self):
    def save_seller_dataframe(result, download_path, keyword):
      # Saves dataframe in CSV file format.
      print("Storing data, almost done....")
      reviews_ratings_df = pd.DataFrame(result)
      # reviews_ratings_df = reviews_ratings_df.iloc[1: ,]
      time.sleep(2)
      # Convert to CSV and save in Downloads.
      if not os.path.exists(download_path):
        os.makedirs(download_path)

      reviews_ratings_df.to_excel(f'{download_path}/{keyword}.xlsx', index=False)

    platform = ""
    if self.radio_kakao.isChecked():
      platform = "Kakao"
    elif self.radio_coupang.isChecked():
      platform = "Coupang"
    elif self.radio_ohouse.isChecked():
      platform = "Ohouse"
    
    keywords = self.input_keywords.text().split(',')

    page = self.input_page.text()

    if platform == "Kakao":
      for keyword in keywords:
        result = scrape_kakao_store(keyword, int(page))
        save_seller_dataframe(result, './result_kakao', keyword)
    elif platform == "Coupang":
      for keyword in keywords:
        result = scrape_coupang(keyword, int(page))
        save_seller_dataframe(result, './result_coupang', keyword)
    elif platform == "Ohouse":
      for keyword in keywords:
        result = scrape_ohouse(keyword, int(page))
        save_seller_dataframe(result, './result_ohouse', keyword)

    print(f"플랫폼: {platform}")
    print(f"검색어: {keywords}")
    print(f"페이지 번호: {page}")
    self.showDialog()