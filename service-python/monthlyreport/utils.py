import datetime, math, pytz
local = pytz.timezone ("Asia/Jakarta")

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
        start_date = datetime.datetime.strptime(start_date+'-0:0:0', '%Y-%m-%d-%H:%M:%S')
        end_date = datetime.datetime.strptime(end_date+'-23:59:59', '%Y-%m-%d-%H:%M:%S')
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
        start_date = datetime.datetime.strptime(start_date+'-0:0:0', '%Y-%m-%d-%H:%M:%S')
        end_date = datetime.datetime.strptime(end_date+'-23:59:59', '%Y-%m-%d-%H:%M:%S')
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

def convertFunc(list_data, totalReport, totalHours):
    dic = { 
            "id":str(list_data[0]),
            "email":list_data[1],
            "username":list_data[2],
            "id_divisi":list_data[3],
            "divisi":list_data[4],
            "id_jabatan":list_data[5],
            "jabatan":list_data[6],
            "fullname":list_data[7],
            "total_report": totalReport,
            "total_hours": totalHours
          }
    return dic

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
