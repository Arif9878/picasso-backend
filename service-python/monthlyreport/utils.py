import pytz
from datetime import datetime
local = pytz.timezone ("Asia/Jakarta")
from jaeger_client import Config
from marshmallow import Schema, fields

busmask_names = 'Mon Tue Wed Thu Fri'
weekmask_names = 'Sat Sun'
class UserResults(Schema):
    id = fields.Str(dump_only=True)
    email = fields.Str(required=True)
    username = fields.Str(dump_only=True)
    id_divisi = fields.Str(dump_only=True)
    divisi = fields.Str(dump_only=True)
    id_jabatan = fields.Str(dump_only=True)
    jabatan = fields.Str(dump_only=True)
    fullname = fields.Str(dump_only=True)

def keys_redis(user_id, key): return '%s-%s' % (user_id, key)

def parse_datetime(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

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

def getListPermit(mongoClient, idUser, numpy, start_date, end_date):
    dbMongo = mongoClient.attendance
    agr = [
        {
            '$match': {
                'createdBy._id': str(idUser), 
                'message': {
                    '$in': [
                        'CUTI', 'SAKIT', 'IZIN'
                    ]
                }
            }
        }, {
            '$group': {
                '_id': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$startDate', 
                        'timezone': 'Asia/Jakarta'
                    }
                }
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
    itm = numpy.array([x['_id'] for x in itm], dtype='datetime64')
    if len(itm) < 0:
        itm = numpy.array([])
    return itm

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
