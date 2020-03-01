from datetime import datetime

import pytz


def parse_datetime_str(datetime_str: str) -> datetime:
    # example = 12/30 21:19:14.526
    year = datetime.today().year
    datetime_str = f'{year}/{datetime_str}000'  # add zeros for microseconds
    return datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S.%f').replace(tzinfo=pytz.timezone('Europe/Berlin'))
