import pytz, jwt
from datetime import datetime
from calendar import monthrange
from jaeger_client import Config

busmask_names = 'Mon Tue Wed Thu Fri'
weekmask_names = 'Sat Sun'

local = pytz.timezone("Asia/Jakarta")

max_time_presence = datetime.strptime('07:30:59', '%H:%M:%S').time()

def keys_redis(user_id, key): return '%s-%s' % (user_id, key)

def parse_datetime(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

def last_day_of_month(date_value):
    return date_value.replace(day = monthrange(date_value.year, date_value.month)[1])

def arrayPresence(totalNoPresence=0,precentageNoPresence=0,totalPresence=0,precentagePresence=0,totalPresenceWeekend=0,precentagePresenceWeekend=0,totalLatePresence=0,precentageLatePresence=0):
    data = {
        'total_no_presence': totalNoPresence,
        'precentage_no_presence': precentageNoPresence,
        'total_presence': totalPresence,
        'precentage_already_presence': precentagePresence,
        'total_weekend_presence': totalPresenceWeekend,
        'precentage_weekend_presence': precentagePresenceWeekend,
        'total_late_presence': totalLatePresence,
        'precentage_late_presence': precentageLatePresence,
    }
    return data

def arrayPermit(permit=0, precentagePermit=0):
    data = {
        'total_permit': permit,
        'precentage_total_permit': precentagePermit,
    }
    return data

def arrayLocationUser(totalWfo=0,precentageWfo=0,totalWfh=0,precentageWfh=0,totalPerjadin=0,precentagePerjadin=0):
    data = {
        'total_wfo': totalWfo,
        'precentage_wfo': precentageWfo,
        'total_wfh': totalWfh,
        'precentage_wfh': precentageWfh,
        'total_perjadin': totalPerjadin,
        'precentage_perjadin': precentagePerjadin,
    }
    return data

def arrayReportUser(totalReportYear=0, totalReportMonth=0):
    data = {
        'total_report_year': totalReportYear,
        'total_report_month': totalReportMonth,
    }
    return data

def arrayOfficeHourUser(totalOfficeHourYear=0, totalOfficeHourMonth=0):
    data = {
        'total_office_hour_year': round(totalOfficeHourYear, 2),
        'total_office_hour_month': round(totalOfficeHourMonth, 2),
    }
    return data

def decode_auth_token(secret_key, auth_token):
    try:
        payload = jwt.decode(auth_token, secret_key)
        return payload
    except jwt.ExpiredSignatureError:
        return 401
    except jwt.InvalidTokenError:
        return 401

def config_jaeger(jaeger_host, jaeger_port):
    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': jaeger_host,
                'reporting_port': jaeger_port,
            },
            'logging': True,
        },
        service_name='dashboard-attendance-user-api',
        validate=True,
    )
    return config
    