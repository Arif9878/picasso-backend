import os, numpy as np, json, datetime, redis, sentry_sdk
from datetime import timedelta
from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from flask_opentracing import FlaskTracing
from sentry_sdk.integrations.flask import FlaskIntegration

from holiday_query import getListHoliday
from utils import (
        busmask_names,
        weekmask_names,
        getCountHours,
        getCountLogbook,
        getListDateLogbook,
        getListPermit,
        UserResults,
        queryAccount,
        config_jaeger,
        keys_redis,
        is_blank,
        parse_datetime
    )

redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)

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
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
    
    get_users_redis = redis_client.get('users')

    if get_users_redis and is_blank(search):
        users = json.loads(get_users_redis)
        result = [data for data in users if data['id_divisi'] == divisi]
    else:
        users = db.session.execute(query)
        if users.returns_rows == False:
            return []
        else:
            result_schema = UserResults()
            result = result_schema.dump(users, many=True)
            # close connection database
            users.close()

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date+'-0:0:0', '%Y-%m-%d-%H:%M:%S')
        end_date = datetime.datetime.strptime(end_date+'-23:59:59', '%Y-%m-%d-%H:%M:%S')

        dateRange = np.arange(np.datetime64(start_date), np.datetime64(end_date+timedelta(days=1)), dtype='datetime64[D]')
        listBusday = np.busdaycalendar(holidays=dateRange, weekmask=busmask_names)
        listHoliday = getListHoliday(mongoClient, np, start_date, end_date)

        # Delete working days if there are holidays
        listBusday = np.array(list(filter(lambda x: x not in listHoliday, listBusday.holidays)))

    for user in result:
        listDayNoLogbook = []
        dataFillingLogbook = 0
        if start_date and end_date:
            get_data_logbook_redis = redis_client.get(keys_redis(user['id'], 'logbooks'))
            get_data_attendance_redis = redis_client.get(keys_redis(user['id'], 'attendances'))

            # Get list date weekend
            listWeekend = np.busdaycalendar(holidays=dateRange, weekmask=weekmask_names)

            # Get list date logbook from redis
            if get_data_logbook_redis and end_date.date() < datetime.datetime.today().replace(day=1).date():
                # filter date logbook by query
                listDateLogbook = np.array([parse_datetime(data['dateTask']).strftime('%Y-%m-%d') for data in json.loads(get_data_logbook_redis) if start_date <= parse_datetime(data['dateTask']) <= end_date], dtype='datetime64')
            else:
                # Get list date logbook from database
                listDateLogbook = getListDateLogbook(mongoClient, user['id'], np, start_date, end_date)

            if get_data_attendance_redis and end_date.date() < datetime.datetime.today().replace(day=1).date():
                # Get list date permit from redis
                listPermit = np.array([parse_datetime(data['startDate']).strftime('%Y-%m-%d') for data in json.loads(get_data_attendance_redis) if start_date <= parse_datetime(data['startDate']) <= end_date and data['message'] in ['CUTI', 'SAKIT', 'IZIN']], dtype='datetime64')
            else:
                # Get list date permit from database
                listPermit = getListPermit(mongoClient, user['id'], np, start_date, end_date)

            # Join array date logbook and array date permit
            listDateLogbook = np.concatenate((listDateLogbook, listPermit))

            # Remove duplicate date logbook
            listDateLogbook = [i for j, i in enumerate(listDateLogbook) if i not in listDateLogbook[:j]]  
            
            # Delete date logbook if there are weekend and holiday
            listDateLogbook = list(np.array(list(filter(lambda x: x not in np.concatenate((listWeekend.holidays, listHoliday)), listDateLogbook))))

            # Logbook list empty days
            listDayNoLogbook = list(np.array(list(filter(lambda x: x not in listDateLogbook, listBusday))))
            dataFillingLogbook = round((len(listDateLogbook)/len(listBusday))*100, 2)
            if len(listDayNoLogbook) > 0:
                listDayNoLogbook = list(np.datetime_as_string(listDayNoLogbook, unit='D'))
        
        totalReport = getCountLogbook(mongoClient, user['id'], start_date, end_date)
        totalHours = getCountHours(mongoClient, user['id'], start_date, end_date)
        
        # add new value on user dictonary
        user['total_report'] = totalReport
        user['total_hours'] = totalHours
        user['precentage_logbook_data_filling'] = dataFillingLogbook
        user['logbook_list_empty_days'] = listDayNoLogbook

    return jsonify(result)

port = os.environ.get('MONTHLY_REPORT_PORT', 80)
if __name__ == '__main__':
      app.run(debug=True, host='0.0.0.0', port=int(port))
