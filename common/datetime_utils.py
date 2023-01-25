from datetime import datetime, timedelta, date
from typing import Union
from numpy import datetime64


def get_week_number(dt: Union[datetime, date]) -> int:
    return dt.isocalendar()[1]


TODAY = date.today()
TODAY_NP = datetime64(TODAY)
CURRENTDAYOFWEEK = TODAY.weekday()
CURRENTWEEKNUMBER = get_week_number(TODAY)
NEXTWEEKNUMBER = get_week_number(TODAY + timedelta(weeks=1))
DATESTAMP = TODAY.strftime("%Y%m%d")
