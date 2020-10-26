import os, json

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from utils import getCountHours, getCountLogbook, convertFunc, queryAccount
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

@app.route('/api/monthly-report/')
def listUserByUnit():
    search = request.args.get('search')
    divisi = request.args.get('divisi')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = queryAccount(divisi=divisi)
    if search:
        query = queryAccount(search='%'+search+'%', divisi=divisi)
    result = db.session.execute(query)
    response = []
    if result.returns_rows == False:
        return response
    else:
        for i in result:
            totalReport = getCountLogbook(mongoClient, i.id, start_date, end_date)
            totalHours = getCountHours(mongoClient, i.id, start_date, end_date)
            response.append(convertFunc(i, totalReport, totalHours))
    return json.dumps(response)

port = os.environ.get('MONTHLY_REPORT_PORT', 80)
if __name__ == '__main__':
      app.run(debug=True, host='0.0.0.0', port=int(port))
