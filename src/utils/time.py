import pytz
from datetime import datetime

def get_current_time():
    time_zone = pytz.timezone("Australia/Melbourne")
    now_datetime = datetime.now(time_zone)
    offset = now_datetime.utcoffset()
    
    return now_datetime, offset