import logging
import datetime

# 현재 날짜와 시간을 불러오기
current_datetime = datetime.datetime.now()

year = current_datetime.year
month = current_datetime.month
day = current_datetime.day
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second

numeric_datetime = f"log/{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}.txt"

# Configure logging here
logging.basicConfig(filename=numeric_datetime, level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)