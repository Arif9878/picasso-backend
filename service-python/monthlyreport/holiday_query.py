from utils import local

def getListHoliday(mongoClient, numpy, start_date, end_date):
    dbMongo = mongoClient.holidaydate
    agr = [
        {
            '$project': {
                '_id': 0, 
                'holiday_date': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$holiday_date'
                    }
                }
            }
        }, {
            '$sort': {
                'holiday_date': 1
            }
        }, {
            '$project': {
                'holiday_date': 1
            }
        }
    ]
    if start_date:
        agr.insert(0, {
            '$match': {
                'holiday_date': {
                    '$gte': local.localize(start_date, is_dst=None),
                    '$lt': local.localize(end_date, is_dst=None)
                }
            }
        })

    itm = list(dbMongo.holidaydate.aggregate(agr))
    listHoliday = numpy.array([x['holiday_date'] for x in itm], dtype='datetime64')
    if len(listHoliday) < 0:
        listHoliday = numpy.array([])
    return listHoliday
