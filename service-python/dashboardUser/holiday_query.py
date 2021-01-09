def getListHoliday(mongoClient, numpy, year, month):
    dbMongo = mongoClient.holidaydate
    agr = [
        {
            '$project': {
                '_id': 0, 
                'year': {
                    '$year': {
                        'date': '$holiday_date', 
                        'timezone': 'Asia/Jakarta'
                    }
                }, 
                'month': {
                    '$month': {
                        'date': '$holiday_date', 
                        'timezone': 'Asia/Jakarta'
                    }
                }, 
                'holiday_date': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$holiday_date'
                    }
                }
            }
        }, {
            '$match': {
                'year': year,
                'month': month
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
    itm = list(dbMongo.holidaydate.aggregate(agr))
    listHoliday = numpy.array([x['holiday_date'] for x in itm], dtype='datetime64')
    if len(listHoliday) < 0:
        listHoliday = numpy.array([])
    return listHoliday
