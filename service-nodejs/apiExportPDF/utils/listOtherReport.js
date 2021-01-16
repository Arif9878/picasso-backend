const Attendance = require('../models/Attendance')
const HolidayDate = require('../models/HolidayDate')

const listAttendance = async (userId, startDate, dueDate) => {
        const sort = {
            startDate: 1,
        }

        const rules = [{
                $match: {
                    'createdBy._id': userId,
                    message: {
                        $in: ['CUTI', 'SAKIT', 'IZIN']
                    },
                    'startDate': {
                        $gte: new Date(startDate),
                        $lt: new Date(dueDate)
                    }
                },
            },
            {
                '$project': {
                    'dateTask': '$startDate',
                    'nameTask': '$message'
                }
            }
        ]

        const result = await Attendance
            .aggregate(rules)
            .sort(sort)

        return result
}

const listHolidayDate = async (startDate, dueDate) => {
        const sort = {
            holiday_date: 1,
        }

        const rules = [{
                $match: {
                    'holiday_date': {
                        $gte: new Date(startDate),
                        $lt: new Date(dueDate)
                    }
                },
            },
            {
                '$project': {
                    'dateTask': '$holiday_date',
                    'type': '$holiday_type',
                    'nameTask': '$holiday_name'
                }
            }
        ]

        const result = await HolidayDate
            .aggregate(rules)
            .sort(sort)
        return result
}

module.exports = {
    listAttendance,
    listHolidayDate
}
