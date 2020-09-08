from datetime import datetime, timedelta
from collections import OrderedDict
try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

def monthlist_short(dates):
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    return OrderedDict(((start + (timedelta(_))).strftime(r"%d/%m/%Y"), None) for _ in xrange(((end+timedelta(days=1)) - start).days)).keys()

def isWeekDay(date):
    date = datetime.strptime(date, '%d/%m/%Y')
    weekno = date.weekday()
    if weekno < 5:
        return True
    else:
        return False