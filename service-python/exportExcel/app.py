import os, io, sentry_sdk
from datetime import datetime, timedelta

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, send_file, request
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from flask_opentracing import FlaskTracing
from sentry_sdk.integrations.flask import FlaskIntegration

from utils import monthlist_short, queryAccount, config_jaeger
from worksheet_format import exportExcelFormatHorizontal, exportExcelFormatVertical

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

@app.route('/api/export-excel/divisi/')
@tracing.trace('path', 'method', 'META', 'path_info', 'content_type')
def exportExcelByDivisi():
    divisi = request.args.get('divisi')
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    dates = [start_date, end_date]

    query = queryAccount(divisi=divisi)
    if search:
        query = queryAccount(search='%'+search+'%', divisi=divisi)
    result = db.session.execute(query)

    listDate = list(monthlist_short(dates))
    memory = io.BytesIO()
    output, nameFile = exportExcelFormatHorizontal(mongoClient, memory, listDate, result)
    output.seek(0)
    # close connection database
    result.close()
    return send_file(output, attachment_filename="%s.xlsx" % nameFile, as_attachment=True)

@app.route('/api/export-excel/category/')
@tracing.trace('path', 'method', 'META', 'path_info', 'content_type')
def exportExcelByCategory():
    divisi = request.args.get('divisi')
    manager_category = request.args.get('manager_category')
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    dates = [start_date, end_date]

    query = queryAccount(divisi=divisi)
    if search:
        query = queryAccount(search='%'+search+'%', divisi=divisi)
    if manager_category:
        query = queryAccount(manager_category='%'+manager_category+'%')
    result = db.session.execute(query)

    listDate = list(monthlist_short(dates))
    memory = io.BytesIO()
    output = exportExcelFormatVertical(mongoClient, memory, listDate, result)
    output.seek(0)
    # close connection database
    result.close()
    return send_file(output, attachment_filename="%s.xlsx" % manager_category, as_attachment=True)

port = os.environ.get('EXPORT_EXCEL_PORT', 80)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(port))
