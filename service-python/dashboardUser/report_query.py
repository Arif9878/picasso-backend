from datetime import datetime
from utils import local

def countReportUserYear(mongoClient, idUser, year):
    dbMongo = mongoClient.logbook
    agr = [
        {
            "createdBy._id": str(idUser)
        }, {
            '$project': {
                '_id': 0, 
                'createdBy': 1,
                'year': {
                    '$year': {
                        'date': '$dateTask', 
                        'timezone': 'Asia/Jakarta'
                    }
                }
            }
        }, {
            '$match': {
                'year': year
            }
        }, {
            '$count': 'count'
        }
    ]

    itm = list(dbMongo.logbooks.aggregate(agr))
    if len(itm) < 1:
        count = 0
    else:
        try:
            count = itm[0]['count']
        except KeyError:
            count = 0
    return count

def countReportUserMonthly(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.logbook
    start_date = datetime.strptime(start_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                'dateTask': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        }, {
            '$count': 'count'
        }
    ]

    itm = list(dbMongo.logbooks.aggregate(agr))
    if len(itm) < 1:
        count = 0
    else:
        try:
            count = itm[0]['count']
        except KeyError:
            count = 0
    return count
