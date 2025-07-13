# Market open utility
from datetime import datetime, time
import pytz

def is_market_open(market):
    now = datetime.now(pytz.timezone('Europe/Oslo'))
    weekday = now.weekday()
    if market == 'oslo':
        # Oslo Børs: 09:00-16:30 CET, Mon-Fri
        open_time = time(9, 0)
        close_time = time(16, 30)
        return 0 <= weekday <= 4 and open_time <= now.time() <= close_time
    elif market == 'global':
        # S&P 500 (New York): 15:30-22:00 CET, Mon-Fri
        open_time = time(15, 30)
        close_time = time(22, 0)
        return 0 <= weekday <= 4 and open_time <= now.time() <= close_time
    return False
