import os, json, datetime, math

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

app = Flask(__name__)

dotenv_path = ''
if exists(join(dirname(__file__), '../../.env')):
    dotenv_path = join(dirname(__file__), '../../.env')
else:
    dotenv_path = join(dirname(__file__), '../.env')

load_dotenv(dotenv_path)

mongoURI = 'mongodb://{dbhost}:{dbport}/'.format(
    dbhost=os.environ.get('DB_MONGO_HOST'),
    dbport=os.environ.get('DB_MONGO_PORT')
)
mongoClient = MongoClient(mongoURI)

postgreURI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'.format(
    dbuser=os.environ.get('DB_USER_AUTH'),
    dbpass=os.environ.get('DB_PASSWORD_AUTH'),
    dbhost=os.environ.get('POSTGRESQL_HOST'),
    dbport=os.environ.get('POSTGRESQL_PORT'),
    dbname=os.environ.get('DB_NAME_AUTH')
)

app.config.update(
    SQLALCHEMY_DATABASE_URI=postgreURI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)

def getCountHours(idUser, start_date, end_date):
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

def getCountLogbook(idUser, start_date, end_date):
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

def conv_func(list_data, totalReport, totalHours):
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

@app.route('/api/monthly-report/')
def listUserByUnit():
    divisi = request.args.get('divisi')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    result = db.session.execute("SELECT accounts_account.id, accounts_account.email, accounts_account.username, accounts_account.first_name, accounts_account.last_name, accounts_account.id_divisi, accounts_account.divisi, accounts_account.id_jabatan, accounts_account.jabatan FROM accounts_account WHERE accounts_account.id_divisi = :divisi", {'divisi': divisi})
    response = []
    if result.returns_rows == False:
        return response
    else:
        for i in result:
            totalReport = getCountLogbook(i.id, start_date, end_date)
            totalHours = getCountHours(i.id, start_date, end_date)
            response.append(conv_func(i, totalReport, totalHours))
    return json.dumps(response)

port = os.environ.get('MONTHLY_REPORT_PORT', 80)
if __name__ == '__main__':
      app.run(debug=True, host='0.0.0.0', port=int(port))