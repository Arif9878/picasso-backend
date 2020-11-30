import numpy as np
import os, io, math
import datetime as dt
from datetime import timedelta

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from utils import AuthUser, getPresence, countPermit, countLocationPresence, countLatePresence, responseDashboard, busmask_names, weekmask_names

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

@app.route('/api/dashboard-user/')
def exportExcelByCategory():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    response = {
        'status': 'fail',
        'message': 'Provide a valid auth token.'
    }
    data = responseDashboard
    if auth_token:
        secret_key = os.environ.get('SECRET_KEY', '')
        user = AuthUser.decode_auth_token(secret_key, auth_token)
        if user != 401:
            start = dt.date( 2020, 11, 1 )
            end = dt.date( 2020, 11, 30 )+timedelta(days=1)

            dateRange = np.arange(np.datetime64(start), np.datetime64(end), dtype='datetime64[D]')
            listBusday = np.busdaycalendar(holidays=dateRange, weekmask=busmask_names)
            listWeekend = np.busdaycalendar(holidays=dateRange, weekmask=weekmask_names)
            presence = 0
            noPresence = 0
            for i in listBusday.holidays:
                if getPresence(mongoClient, user['user_id'], str(i)):
                    presence += 1
                else:
                    noPresence += 1
            presenceWeekend = 0
            for i in listWeekend.holidays:
                if getPresence(mongoClient, user['user_id'], str(i)):
                    presenceWeekend += 1

            days = np.busday_count( start, end )

            permit = countPermit(mongoClient, user['user_id'], str(start), str(end))
            totalLatePresence = countLatePresence(mongoClient, user['user_id'], str(start), str(end))
            totalWfh = countLocationPresence(mongoClient, user['user_id'], "WFH", str(start), str(end))
            totalWfo = countLocationPresence(mongoClient, user['user_id'], "WFO", str(start), str(end))
            precentagePresence = round(float(presence-permit)/float(days)*100, 2)
            precentageLatePresence = round(float(totalLatePresence)/float(days)*100, 2)
            precentagePermit = round(float(permit)/float(days) *100, 2)
            precentageNoPresence = round(float(noPresence)/float(days) * 100, 2)
            precentagePresenceWeekend = round(float(presenceWeekend)/float(len(listWeekend.holidays)) * 100, 2)
            precentageWfo = round(float(totalWfo)/float(days) * 100, 2)
            precentageWfh = round(float(totalWfh)/float(days) * 100, 2)
            data = responseDashboard(
                        noPresence,
                        precentageNoPresence,
                        presence,
                        precentagePresence,
                        permit,
                        precentagePermit,
                        presenceWeekend,
                        precentagePresenceWeekend,
                        totalLatePresence,
                        precentageLatePresence,
                        totalWfo,
                        precentageWfo,
                        totalWfh,
                        precentageWfh
                    )
    return jsonify(
                message="success",
                data=data,
                status=200
            )

port = os.environ.get('DASHBOARD_USER_PORT', 80)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(port))
