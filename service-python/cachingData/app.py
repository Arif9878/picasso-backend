import os, boto3, redis, json
from os.path import join, dirname, exists
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_sqlalchemy import SQLAlchemy
from utils import getListLogbook, getListAttendance, putToS3, getFromS3, queryAccount, UserResults
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

app = Flask(__name__)

dotenv_path = ''
if exists(join(dirname(__file__), '../../.env')):
    dotenv_path = join(dirname(__file__), '../../.env')
else:
    dotenv_path = join(dirname(__file__), '../.env')

load_dotenv(dotenv_path)

redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)

mongoURI = 'mongodb://{dbhost}:{dbport}/'.format(
    dbhost=os.environ.get('DB_MONGO_HOST'),
    dbport=os.environ.get('DB_MONGO_PORT')
)

mongo_client = MongoClient(mongoURI)

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

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
)

def set_key_redis(user_id, key): return '%s-%s' % (user_id, key)

def dumpToS3():
    list_logbooks = getListLogbook(mongo_client)
    list_attendances =  getListAttendance(mongo_client)
    putToS3(s3, os.environ.get('AWS_S3_BUCKET'), os.environ.get('DUMP_DATA_LOGBOOKS'), json.dumps(list_logbooks))
    putToS3(s3, os.environ.get('AWS_S3_BUCKET'), os.environ.get('DUMP_DATA_ATTENDANCES'), json.dumps(list_attendances))

def cacheToRedis():
    json_logbooks = getFromS3(s3, os.environ.get('AWS_S3_BUCKET'), os.environ.get('DUMP_DATA_LOGBOOKS'))
    json_attendances = getFromS3(s3, os.environ.get('AWS_S3_BUCKET'), os.environ.get('DUMP_DATA_ATTENDANCES'))
    get_users_redis = redis_client.get('users')
    if get_users_redis:
        result = json.loads(get_users_redis)
    else:
        query_user = queryAccount()
        users = db.session.execute(query_user)
        result_schema = UserResults()
        result = result_schema.dump(users, many=True)
        # close connection database
        users.close()
    for user in result:
        logbooks = [data for data in json.loads(json_logbooks) if data['createdById']==user['id']]
        attendances = [data for data in json.loads(json_attendances) if data['createdById']==user['id']]
        redis_client.set(set_key_redis(user['id'], 'logbooks'), json.dumps(logbooks))
        redis_client.set(set_key_redis(user['id'], 'attendances'), json.dumps(attendances))

def cacheUser():
    query_user = queryAccount()        
    users = db.session.execute(query_user)
    result_schema = UserResults()
    result = result_schema.dump(users, many=True)
    # close connection database
    users.close()
    redis_client.set('users', json.dumps(result))

sched = BackgroundScheduler(daemon=True)
sched.add_job(dumpToS3, 'interval', hours=2)
sched.add_job(cacheToRedis, 'interval', hours=1)
sched.add_job(cacheUser, 'interval', hours=2)
sched.start()

port = os.environ.get('CACHING_DATA_PORT', 80)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(port))
