def getCountHours(mongoClient, idUser, start_date, end_date):
    dbMongo = mongoClient.attendance
    agr = [
        {
            '$match': {
                "createdBy._id": str(idUser)
            }
        }, {
            '$group': {
                '_id': 0, 
                'count': {
                    '$sum': '$officeHours'
                }
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
                'startDate': {
                    '$gte': datetime.datetime.strptime(start_date+'-0:0:0', '%Y-%m-%d-%H:%M:%S'),
                    '$lt': datetime.datetime.strptime(end_date+'-23:59:59', '%Y-%m-%d-%H:%M:%S')
                }
            }
        })

    itm = list(dbMongo.attendances.aggregate(agr))
    if not itm:
      count = 0
    else:
      count = math.ceil(itm[0]['count'])
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
                    '$gte': datetime.datetime.strptime(start_date+'-0:0:0', '%Y-%m-%d-%H:%M:%S'),
                    '$lt': datetime.datetime.strptime(end_date+'-23:59:59', '%Y-%m-%d-%H:%M:%S')
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
            "fullname":list_data[3]+' '+list_data[4],
            "id_divisi":list_data[5],
            "divisi":list_data[6],
            "id_jabatan":list_data[7],
            "jabatan":list_data[8],
            "total_report": totalReport,
            "total_hours": totalHours
          }
    return dic

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