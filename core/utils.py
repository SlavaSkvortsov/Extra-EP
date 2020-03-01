from datetime import datetime

import pytz


def parse_datetime_str(datetime_str: str) -> datetime:
    # example = 12/30 21:19:14.526
    datetime_str = f'{datetime_str}000'  # add zeros for microseconds
    today = datetime.today()
    return datetime.strptime(datetime_str, '%m/%d %H:%M:%S.%f').replace(
        year=today.year, tzinfo=pytz.timezone('Europe/Berlin'),
    )
