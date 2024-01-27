import logging
import datetime
import os

# 현재 날짜와 시간을 불러오기
current_datetime = datetime.datetime.now()

year = current_datetime.year
month = current_datetime.month
day = current_datetime.day
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second

if not os.path.exists('log'):
  os.makedirs('log')

numeric_datetime = f"log/{year:04d}년{month:02d}월{day:02d}일{hour:02d}시{minute:02d}분{second:02d}초.txt"
# Configure logging here
logging.basicConfig(filename=numeric_datetime, level=logging.INFO, format='%(asctime)s - %(message)s')

logger = logging.getLogger(__name__)
