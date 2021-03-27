def getListLogbook(mongo_client):
    dbMongo = mongo_client.logbook
    agr = [
      {
        '$project': {
          '_id':  { '$toString': "$_id" },
          'dateTask': { '$dateToString': { 'format': '%Y-%m-%dT%H:%M:%SZ', 'date': '$dateTask', 'timezone': 'Asia/Jakarta' } },
          'projectId': 1,
          'projectName': 1,
          'nameTask': 1,
          'isDocumentLink': 1,
          'isMainTask': 1,
          'workPlace': 1,
          'organizerTask': 1,
          'difficultyTask': { '$ifNull': [ '$difficultyTask', '' ] },
          'evidenceTaskURL': '$evidenceTask.fileURL',
          'evidenceTaskPath': '$evidenceTask.filePath',
          'documentTaskURL': { '$ifNull': ['$documentTask.fileURL', ''] },
          'documentTaskPath': { '$ifNull': [ '$documentTask.filePath', '' ] },
          'tupoksiJabatanId': { '$ifNull': ['$tupoksiJabatanId', ''] },
          'tupoksiJabatanName': { '$ifNull': ['$tupoksiJabatanName', ''] },
          'otherInformation': { '$ifNull': ['$otherInformation', ''] },
          'createdById': '$createdBy._id'
        }
      }, {
          '$sort': {
            'dateTask': 1
          }
      }
    ]
    itm = list(dbMongo.logbooks.aggregate(agr))
    return itm

def getListAttendance(mongo_client):
    dbMongo = mongo_client.attendance
    agr = [
      {
        '$project': {
          '_id':  { '$toString': "$_id" },
          'startDate': { '$dateToString': { 'format': '%Y-%m-%dT%H:%M:%SZ', 'date': '$startDate', 'timezone': 'Asia/Jakarta' } },
          'endDate': { '$dateToString': { 'format': '%Y-%m-%dT%H:%M:%SZ', 'date': '$endDate', 'timezone': 'Asia/Jakarta' } },
          'officeHours': 1,
          'location': 1,
          'message': 1,
          'createdById': '$createdBy._id'
        }
      }, {
          '$sort': {
            'startDate': 1
          }
      }
    ]
    itm = list(dbMongo.attendances.aggregate(agr))
    return itm

def putToS3(s3, bucket, key, data):
    s3.put_object(Bucket=bucket, Key=key, Body=data)

def getFromS3(s3, bucket, key):
    object = s3.get_object(Bucket=bucket, Key=key)
    return object['Body'].read()

def queryAccount(is_active=True):
    query = """
        SELECT
            accounts_account.id,
            accounts_account.is_active
        FROM
            accounts_account
        WHERE
            accounts_account.is_active = '%s'
        ORDER BY id ASC
    """ % (is_active)

    return query