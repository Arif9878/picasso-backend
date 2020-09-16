import math
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


def getHours(mongoClient, idUser, date):
    dbMongo = mongoClient.attendance
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                'startDate': {
                    '$gte': datetime.strptime(date+'-00:00:00', '%d/%m/%Y-%H:%M:%S'),
                    '$lt': datetime.strptime(date+'-23:59:59', '%d/%m/%Y-%H:%M:%S')
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'officeHours': 1
            }
        }
    ]

    itm = list(dbMongo.attendances.aggregate(agr))
    if not itm:
        count = 0
    else:
        count = math.ceil(itm[0]['officeHours'])
    return count

def getInformation(mongoClient, idUser, date):
    dbMongo = mongoClient.attendance
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                'startDate': {
                    '$gte': datetime.strptime(date+'-00:00:00', '%d/%m/%Y-%H:%M:%S'),
                    '$lt': datetime.strptime(date+'-23:59:59', '%d/%m/%Y-%H:%M:%S')
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'location': 1,
                'message': 1
            }
        }
    ]

    itm = list(dbMongo.attendances.aggregate(agr))
    if not itm:
        information = '-'
    else:
        information = itm[0]['message']+' ('+itm[0]['location']+')'
    return information

def queryAccount(divisi=None):
    query = """
        SELECT
            accounts_account.id,
            accounts_account.email,
            accounts_account.username,
            accounts_account.first_name,
            accounts_account.last_name,
            accounts_account.id_divisi,
            accounts_account.divisi,
            accounts_account.id_jabatan,
            accounts_account.jabatan
        FROM
            accounts_account
        WHERE
            accounts_account.id_divisi = '%s'
    """ % divisi

    return query
