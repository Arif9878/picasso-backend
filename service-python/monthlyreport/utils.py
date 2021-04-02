import pytz
local = pytz.timezone ("Asia/Jakarta")
from jaeger_client import Config

def getCountHours(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.attendance
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser)
            }
        },  {
            '$project': {
                'officeHours': 1
            }
        },  {
            '$group': {
                '_id': 0, 
                'count': {
                    '$sum': '$officeHours'
                }
            }
        },  {
            '$project': {
                '_id': 0
            }
        }
    ]

    if start_date:
        agr.insert(0, {
            '$match': {
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        })

    itm = list(dbMongo.attendances.aggregate(agr))
    if not itm:
      count = 0
    else:
      count = itm[0]['count']
    return count

def getCountLogbook(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.logbook
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser)
            }
        }, {
            '$group': {
                '_id': 0, 
                'count': { '$sum': { '$cond': [ { '$eq': [ "$_id", "none" ] }, 0, 1 ] } }
            }
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]

    if start_date:
        agr.insert(0, {
            '$match': {
                'dateTask': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        })

    itm = list(dbMongo.logbooks.aggregate(agr))
    if not itm:
      count = 0
    else:
      count = itm[0]['count']
    return count

def getListDateLogbook(mongoClient, idUser, numpy, start_date, end_date):
    dbMongo = mongoClient.logbook
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser)
            }
        }, {
        '$group': {
            '_id': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$dateTask', 
                        'timezone': 'Asia/Jakarta'
                    }
                }
            }
        }, {
            '$project': {
                '_id': 1
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }
    ]

    if start_date:
        agr.insert(0, {
            '$match': {
                'dateTask': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        })


    itm = list(dbMongo.logbooks.aggregate(agr))
    itm = numpy.array([x['_id'] for x in itm], dtype='datetime64')
    if len(itm) < 0:
        itm = numpy.array([])
    return itm

def convertFunc(list_data, totalReport, totalHours, dataFillingLogbook, listDayNoLogbook):
    dict = { 
            "id":str(list_data[0]),
            "email":list_data[1],
            "username":list_data[2],
            "id_divisi":list_data[3],
            "divisi":list_data[4],
            "id_jabatan":list_data[5],
            "jabatan":list_data[6],
            "fullname":list_data[7],
            "total_report": totalReport,
            "total_hours": totalHours,
            "precentage_logbook_data_filling": dataFillingLogbook,
            "logbook_list_empty_days": listDayNoLogbook
          }
    return dict

def queryAccount(search='%', divisi=None, is_active=True):
    query = """
        SELECT
            accounts_account.id,
            accounts_account.email,
            accounts_account.username,
            accounts_account.id_divisi,
            accounts_account.divisi,
            accounts_account.id_jabatan,
            accounts_account.jabatan,
            CONCAT(first_name,' ',last_name) AS fullname
        FROM
            accounts_account
        WHERE
            accounts_account.id_divisi = '%s'
        AND
            accounts_account.is_active = '%s'
        AND
            LOWER(CONCAT(first_name,' ',last_name)) LIKE LOWER('%s')
        ORDER BY divisi ASC
    """ % (divisi, is_active, search)

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
        service_name='monthly-report-user-api',
        validate=True,
    )
    return config
