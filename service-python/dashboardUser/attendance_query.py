from datetime import datetime
from utils import local

def getPresence(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(start_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
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
                '_id': 1,
                'startDate': { '$dateToString': { 'format': '%Y-%m-%dT%H:%M:%SZ', 'date': '$startDate', 'timezone': 'Asia/Jakarta' } },
                'endDate': { '$dateToString': { 'format': '%Y-%m-%dT%H:%M:%SZ', 'date': '$endDate', 'timezone': 'Asia/Jakarta' } },
                'officeHours': 1,
                'location': 1,
                'message': 1
            }
        }
    ]
    itm = list(dbMongo.attendances.aggregate(agr))
    if len(itm) < 0:
        itm = []
    return itm

def countOfficeHourUserYear(mongoClient, idUser, year):
    dbMongo = mongoClient.attendance
    agr = [
        {
            '$project': {
                'year': {
                    '$year': {
                        'date': '$startDate', 
                        'timezone': 'Asia/Jakarta'
                    }
                }, 
                'createdBy': 1, 
                'officeHours': 1
            }
        }, {
            '$match': {
                "createdBy._id": str(idUser),
                'year': year
            }
        }, {
            '$group': {
                '_id': 0, 
                'count': {
                    '$sum': '$officeHours'
                }
            }
        }
    ]

    itm = list(dbMongo.attendances.aggregate(agr))
    if len(itm) < 1:
        count = 0
    else:
        try:
            count = itm[0]['count']
        except KeyError:
            count = 0
    return count

def countOfficeHourUserMonthly(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(start_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
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
            '$group': {
                '_id': 0, 
                'count': {
                    '$sum': '$officeHours'
                }
            }
        }
    ]

    itm = list(dbMongo.attendances.aggregate(agr))
    if len(itm) < 1:
        count = 0
    else:
        try:
            count = itm[0]['count']
        except KeyError:
            count = 0
    return count
