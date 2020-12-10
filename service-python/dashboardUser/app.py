import numpy as np
import os, io, math
import datetime as dt
from datetime import timedelta

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from utils import (
        arrayPresence,
        arrayPermit,
        arrayLocationUser,
        arrayReportUser,
        arrayOfficeHourUser,
        decode_auth_token,
        busmask_names,
        last_day_of_month,
        weekmask_names
    )
from attendance_query import (
        getPresence,
        countPermit,
        countLocationPresence,
        countLatePresence,
        countOfficeHourUserYear,
        countOfficeHourUserMonthly
    )
from report_query import countReportUserYear, countReportUserMonthly
from holiday_query import getListHoliday

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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

@app.route('/api/dashboard/attendance-user')
def dashboardAttendanceUser():
    month = request.args.get('month')
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    response = jsonify({'message': 'Provide a valid auth token.'}), 401
    if auth_token:
        secret_key = os.environ.get('SECRET_KEY', '')
        user = decode_auth_token(secret_key, auth_token)
        data = {}
        if user != 401:
            today = dt.datetime.today().date()
            start = dt.datetime(year=today.year, month=today.month, day=1).date()
            if month: 
                start = dt.datetime(year=today.year, month=int(month), day=1).date()
            end = last_day_of_month(start)+timedelta(days=1)
            dateRange = np.arange(np.datetime64(start), np.datetime64(end), dtype='datetime64[D]')
            dateRangeFromNow = np.arange(np.datetime64(start), np.datetime64(today+timedelta(days=1)), dtype='datetime64[D]')
            listBusdayFromNow = np.busdaycalendar(holidays=dateRangeFromNow, weekmask=busmask_names)
            listBusday = np.busdaycalendar(holidays=dateRange, weekmask=busmask_names)
            listWeekend = np.busdaycalendar(holidays=dateRange, weekmask=weekmask_names)
            listHoliday = getListHoliday(mongoClient, np, start.year, start.month)

            # Delete working days if there are holidays
            listBusdayFromNow = np.array(list(filter(lambda x: x not in listHoliday, listBusdayFromNow.holidays)))
            listBusday = np.array(list(filter(lambda x: x not in listHoliday, listBusday.holidays)))

            presence = 0
            noPresence = 0
            if month == None or today.month == int(month):
                for i in listBusdayFromNow:
                    if getPresence(mongoClient, user['user_id'], str(i)):
                        presence += 1
                    else:
                        noPresence += 1
            else:
                for i in listBusday:
                    if getPresence(mongoClient, user['user_id'], str(i)):
                        presence += 1
                    else:
                        noPresence += 1

            presenceWeekend = 0
            for i in listWeekend.holidays:
                if getPresence(mongoClient, user['user_id'], str(i)):
                    presenceWeekend += 1
            busDaysFromNow = len(listBusdayFromNow)
            busDays = len(listBusday)
            weekEnd = len(listWeekend.holidays)

            permit = countPermit(mongoClient, user['user_id'], str(start), str(end))
            latePresence = countLatePresence(mongoClient, user['user_id'], str(start), str(end))
            totalWfh = countLocationPresence(mongoClient, user['user_id'], "WFH", str(start), str(end))
            totalWfo = countLocationPresence(mongoClient, user['user_id'], "WFO", str(start), str(end))
            totalPerjadin = countLocationPresence(mongoClient, user['user_id'], "PERJADIN", str(start), str(end))
            precentagePresence = round(float(presence-permit)/float(busDays)*100, 2)
            precentageLatePresence = round(float(latePresence)/float(busDays)*100, 2)
            precentagePermit = round(float(permit)/float(busDays) *100, 2)
            precentageNoPresence = round(float(noPresence)/float(busDays) * 100, 2)
            precentagePresenceWeekend = round(float(presenceWeekend)/float(weekEnd) * 100, 2)
            precentageWfo = round(float(totalWfo)/float(busDays) * 100, 2)
            precentageWfh = round(float(totalWfh)/float(busDays) * 100, 2)
            precentagePerjadin = round(float(totalPerjadin)/float(busDays) * 100, 2)
            array_presence = arrayPresence(noPresence,precentageNoPresence,presence-permit,precentagePresence,presenceWeekend,precentagePresenceWeekend,latePresence,precentageLatePresence)
            array_permit = arrayPermit(permit, precentagePermit)
            array_location_user = arrayLocationUser(totalWfo,precentageWfo,totalWfh,precentageWfh,totalPerjadin,precentagePerjadin)
            
            data.update(array_presence)
            data.update(array_permit)
            data.update(array_location_user)
            
        response = jsonify(message="success", data=data, status=200)

    return response

@app.route('/api/dashboard/report-user')
def dashboardReportUser():
    month = request.args.get('month')
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    response = jsonify({'message': 'Provide a valid auth token.'}), 401
    if auth_token:
        secret_key = os.environ.get('SECRET_KEY', '')
        user = decode_auth_token(secret_key, auth_token)
        data = {}
        if user != 401:
            today = dt.datetime.today().date()
            start = dt.datetime(year=today.year, month=today.month, day=1).date()
            if month: 
                start = dt.datetime(year=today.year, month=int(month), day=1).date()
            end = last_day_of_month(start)+timedelta(days=1)

            totalOfficeHourUserYear = countOfficeHourUserYear(mongoClient, user['user_id'], today.year)
            totalOfficeHourUserMonthly = countOfficeHourUserMonthly(mongoClient, user['user_id'], str(start), str(end))
            totalReportUserYear = countReportUserYear(mongoClient, user['user_id'], today.year)
            totalReportUserMonthly = countReportUserMonthly(mongoClient, user['user_id'], str(start), str(end))
            array_report_user = arrayReportUser(totalReportUserYear, totalReportUserMonthly)
            array_office_hour_user = arrayOfficeHourUser(totalOfficeHourUserYear, totalOfficeHourUserMonthly)
            data.update(array_report_user)
            data.update(array_office_hour_user)
            
        response = jsonify(message="success", data=data, status=200)

    return response

port = os.environ.get('DASHBOARD_USER_PORT', 80)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(port))
