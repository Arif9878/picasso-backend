import math, pytz, jwt
from datetime import datetime

    
busmask_names = 'Mon Tue Wed Thu Fri'
weekmask_names = 'Sat Sun'

local = pytz.timezone("Asia/Jakarta")

def responseDashboard(
    noPresence=0,
    precentageNoPresence=0,
    presence=0,
    precentagePresence=0,
    permit=0,
    precentagePermit=0,
    presenceWeekend=0,
    precentagePresenceWeekend=0,
    totalLatePresence=0,
    precentageLatePresence=0,
    totalWfo=0,
    precentageWfo=0,
    totalWfh=0,
    precentageWfh=0):
    data = {
        'total_no_presence': noPresence,
        'precentage_no_presence': precentageNoPresence,
        'total_presence': presence-permit,
        'precentage_already_presence': precentagePresence,
        'total_permit': permit,
        'precentage_total_permit': precentagePermit,
        'total_weekend_presence': presenceWeekend,
        'precentage_weekend_presence': precentagePresenceWeekend,
        'total_late_presence': totalLatePresence,
        'precentage_late_presence': precentageLatePresence,
        'total_wfo': totalWfo,
        'precentage_wfo': precentageWfo,
        'total_wfh': totalWfh,
        'precentage_wfh': precentageWfh,
    }
    return data

class AuthUser:
    @staticmethod
    def decode_auth_token(secret_key, auth_token):
        try:
            payload = jwt.decode(auth_token, secret_key)
            return payload
        except jwt.ExpiredSignatureError:
            return 401
        except jwt.InvalidTokenError:
            return 401


def getPresence(mongoClient, idUser, date):
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
                '$addFields': {
                    'date': {
                        '$dateToString': {
                            'format': '%Y-%m-%d %H:%M:%S', 
                            'timezone': 'Asia/Jakarta', 
                            'date': '$startDate'
                        }
                    }, 
                    'isLate': {
                        '$and': [
                            {
                                '$gte': [
                                    {
                                        '$hour': '$startDate'
                                    }, 1
                                ]
                            }, {
                                '$gte': [
                                    {
                                        '$minute': '$startDate'
                                    }, 1
                                ]
                            }, {
                                '$gte': [
                                    {
                                        '$second': '$startDate'
                                    }, 0
                                ]
                            }
                        ]
                    }
                }
            }, {
                '$match': {
                    'isLate': True, 
                    "createdBy._id": str(idUser),
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
