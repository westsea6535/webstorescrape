from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QRadioButton
from PyQt5.QtGui import QIntValidator
from kakao import scrape_kakao_store
from coupang import scrape_coupang

class guiForm(QWidget):
  def __init__(self):
    super().__init__()
    self.init_ui()

  def init_ui(self):
    # 위젯 생성
    self.label_platform = QLabel('스토어 선택')
    self.radio_kakao = QRadioButton('Kakao')
    self.radio_coupang = QRadioButton('Coupang')

    self.label_keywords = QLabel('검색어:')
    self.input_keywords = QLineEdit()

    self.label_page = QLabel('페이지 개수')
    self.input_page = QLineEdit()
    self.input_page.setValidator(QIntValidator(1, 9))  # 숫자만 입력 가능하도록 설정

    self.button_search = QPushButton('확인')

    # 레이아웃 생성 및 위젯 추가
    layout = QVBoxLayout()
    layout.addWidget(self.label_platform)
    layout.addWidget(self.radio_kakao)
    layout.addWidget(self.radio_coupang)

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
    self.setGeometry(1000, 1000, 1000, 300)
    self.setFixedSize(1000, 300)

  def onButtonClick(self):
    platform = "Kakao" if self.radio_kakao.isChecked() else "Coupang"
    keywords = self.input_keywords.text().split(',')
    page = self.input_page.text()
    if platform == "Kakao":
      for keyword in keywords:
        scrape_kakao_store(keyword, int(page))
    elif platform == "Coupang":
      for keyword in keywords:
        scrape_coupang(keyword, int(page))

    # 여기에 검색 결과를 처리하는 코드를 추가하세요.
    print(f"플랫폼: {platform}")
    print(f"검색어: {keywords}")
    print(f"페이지 번호: {page}")