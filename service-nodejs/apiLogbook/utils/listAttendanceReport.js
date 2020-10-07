const Attendance = require('../models/Attendance')

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

module.exports = {
    listAttendance
}
