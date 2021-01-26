import math, pytz
from datetime import datetime, timedelta
from collections import OrderedDict
from jaeger_client import Config

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

local = pytz.timezone("Asia/Jakarta")

def monthlist_short(dates):
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    return OrderedDict(((start + (timedelta(_))).strftime(r"%Y-%m-%d"), None) for _ in xrange(((end+timedelta(days=1)) - start).days)).keys()

def isWeekDay(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    weekno = date.weekday()
    if weekno < 5:
        return True
    else:
        return False

def getTimePresence(mongoClient, idUser, date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'checkin': { '$dateToString': { 'format': "%H:%M", 'date': "$startDate", 'timezone': "Asia/Jakarta" }},
                'checkout': { '$dateToString': { 'format': "%H:%M", 'date': "$endDate", 'timezone': "Asia/Jakarta" }}
            }
        }
    ]
    itm = list(dbMongo.attendances.aggregate(agr))
    time = ['-', '-']
    if not itm:
        time = ['-', '-']
    else:
        try:
            checkin = itm[0]['checkin']
            checkout = itm[0]['checkout']
            time = [checkin, checkout]
        except KeyError:
            time = ['-', '-']
    return time

def getHours(mongoClient, idUser, date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
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
        try:
            count = itm[0]['officeHours']
        except KeyError:
            count = 0
    return count

def getInformation(mongoClient, idUser, date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
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

def queryAccount(divisi=None, manager_category=None, search='%', is_active=True):
    query = """
        SELECT
            accounts_account.id,
            CONCAT(first_name,' ',last_name) AS fullname,
            accounts_account.id_divisi,
            accounts_account.divisi,
            accounts_account.id_jabatan,
            accounts_account.jabatan,
            accounts_account.manager_category
        FROM
            accounts_account
        WHERE
            accounts_account.id_divisi = '%s'
        OR
            LOWER(accounts_account.manager_category) LIKE LOWER('%s')
        AND
            LOWER(CONCAT(first_name,' ',last_name)) LIKE LOWER('%s')
        AND
            accounts_account.is_active = '%s'
    """ % (divisi, manager_category, search, is_active)

    return query

def config_jaeger(jaeger_host, jaeger_port):
    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': jaeger_host,
                'reporting_port': jaeger_port,
            },
            'logging': True,
        },
        service_name='export-excel-api',
        validate=True,
    )
    return config
