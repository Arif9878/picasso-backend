from datetime import datetime
from utils import local

def getPresence(mongoClient, idUser, date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                'createdBy._id': str(idUser),
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        }, {
            '$project': {
                '_id': 1,
            }
        }
    ]
    itm = list(dbMongo.attendances.aggregate(agr))
    exist = False
    if len(itm) > 0:
        exist = True
    return exist

def countPermit(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(start_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                'createdBy._id': idUser,
                'message': {
                    '$in': ['CUTI', 'SAKIT', 'IZIN']
                },
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        }, {
            '$count': 'count'
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

def countLocationPresence(mongoClient, idUser, location, start_date, end_date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(start_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser),
                "location": location,
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        },  {
            '$count': 'count'
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

def countLatePresence(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.attendance
    start_date = datetime.strptime(start_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date+' 23:59:59', '%Y-%m-%d %H:%M:%S')
    agr = [
        {
            '$match': {
                'createdBy._id': str(idUser), 
                'startDate': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        },
        {
            '$project': {
                'createdBy': 1, 
                'startDate': 1, 
                'hours': {
                    '$add': [
                        {
                            '$hour': {
                                'date': '$startDate', 
                                'timezone': 'Asia/Jakarta'
                            }
                        }
                    ]
                }, 
                'minutes': {
                    '$add': [
                        {
                            '$minute': {
                                'date': '$startDate', 
                                'timezone': 'Asia/Jakarta'
                            }
                        }
                    ]
                }
            }
        }, {
            '$match': {
                'hours' : { '$gte' : 7  },
                'minutes' : { '$gte' : 31  },
            }
        }, {
            '$count': 'count'
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

def countOfficeHourUserYear(mongoClient, idUser, year):
    dbMongo = mongoClient.attendance
    agr = [
         {
            '$match': {
                "createdBy._id": str(idUser)
            }
        },{
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
                'createdBy._id': str(idUser),
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
