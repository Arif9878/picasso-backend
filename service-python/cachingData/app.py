import os, boto3, redis, json
from os.path import join, dirname, exists
from dotenv import load_dotenv
from pymongo import MongoClient
from utils import getListLogbook, getListAttendance, putToS3, getFromS3
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

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

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
)

def dumpToS3():
    list_logbooks = getListLogbook(mongo_client)
    list_attendances =  getListAttendance(mongo_client)
    putToS3(s3, os.environ.get('AWS_S3_BUCKET'), 'dump-data/logbooks', json.dumps(list_logbooks))
    putToS3(s3, os.environ.get('AWS_S3_BUCKET'), 'dump-data/attendances', json.dumps(list_attendances))

def cacheToRedis():
    json_logbooks = getFromS3(s3, os.environ.get('AWS_S3_BUCKET'), 'dump-data/logbooks')
    json_attendances = getFromS3(s3, os.environ.get('AWS_S3_BUCKET'), 'dump-data/attendances')
    redis_client.set('cache-logbooks', json_logbooks)
    redis_client.set('cache-attendances', json_attendances)

sched = BackgroundScheduler(daemon=True)
sched.add_job(dumpToS3, 'cron', hour=1, minute=0, second=1)
sched.add_job(cacheToRedis, 'interval', minutes=30)
sched.start()

app = Flask(__name__)

if __name__ == "__main__":
    app.run()