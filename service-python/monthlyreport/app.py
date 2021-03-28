import os, json, sentry_sdk

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from flask_opentracing import FlaskTracing
from sentry_sdk.integrations.flask import FlaskIntegration

from utils import getCountHours, getCountLogbook, convertFunc, queryAccount, config_jaeger

dotenv_path = ''
if exists(join(dirname(__file__), '../../.env')):
    dotenv_path = join(dirname(__file__), '../../.env')
else:
    dotenv_path = join(dirname(__file__), '../.env')

load_dotenv(dotenv_path)

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN_FLASK'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

app = Flask(__name__)

jaeger_host = os.environ.get('JAEGER_HOST')
jaeger_port = os.environ.get('JAEGER_PORT')

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
    SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    SQLALCHEMY_DATABASE_URI=postgreURI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_POOL_SIZE=10,
    SQLALCHEMY_MAX_OVERFLOW=20,
    SQLALCHEMY_POOL_RECYCLE=1800
)

db = SQLAlchemy(app)

jaeger_tracer = config_jaeger(jaeger_host, jaeger_port).initialize_tracer()
tracing = FlaskTracing(jaeger_tracer)

@app.route('/api/monthly-report/')
@tracing.trace('path', 'method', 'META', 'path_info', 'content_type')
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
