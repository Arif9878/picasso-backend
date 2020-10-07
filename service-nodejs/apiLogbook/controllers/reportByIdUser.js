const {
    errors,
    APIError
} = require('../utils/exceptions')
const { 
    generateReport,
    reportForm 
} = require('../utils/generateReport')
const {
    listAttendance
} = require('../utils/listAttendanceReport')
const LogBook = require('../models/LogBook')
const moment = require('moment')
const servers_nats = [process.env.NATS_URI]
const nats = require('nats').connect({
    'servers': servers_nats
})
// eslint-disable-next-line
module.exports = async (req, res, next) => {
    try {
        let sort = {
            dateTask: 1,
        }
        const {
            userId
        } = req.params

        const {
            start_date,
            end_date
        } = req.query

        const dueDate = moment(end_date).add(1,'days').format('YYYY-MM-DD')

        if (!userId) throw new APIError(errors.serverError)

        const rules = [{
                $match: {
                    'createdBy._id': userId,
                    'dateTask': {
                        $gte: new Date(start_date),
                        $lt: new Date(dueDate)
                    }
                },
            },
            {
                '$lookup': {
                    'from': 'blobsfiles',
                    'localField': '_id',
                    'foreignField': 'logBookId',
                    'as': 'blobsEvidence'
                }
            },
            {
                '$unwind': {
                    'path': '$blobsEvidence',
                    'includeArrayIndex': 'arrayIndex'
                }
            },
            {
                '$project': {
                    'dateTask': 1,
                    'projectId': 1,
                    'projectName': 1,
                    'nameTask': 1,
                    'difficultyTask': 1,
                    'isDocumentLink': 1,
                    'isMainTask': 1,
                    'organizerTask': 1,
                    'otherInformation': 1,
                    'workPlace': 1,
                    'evidenceTaskPath': '$evidenceTask.filePath',
                    'evidenceTaskURL': '$evidenceTask.fileURL',
                    'evidenceBlob': '$evidenceTask.fileBlob',
                    'documentTaskPath': '$documentTask.filePath',
                    'documentTaskURL': '$documentTask.fileURL',
                    'blobsEvidence': '$blobsEvidence.blob'
                }
            }
        ]

        // Get logbook
        const logBook = await LogBook
            .aggregate(rules)
            .sort(sort)
        const attendance = await listAttendance(userId, start_date, dueDate)
        logBook.push(...attendance)
        logBook.sort(function (a, b) {
            return new Date(a.dateTask) - new Date(b.dateTask)
        })
        // Get logbook per Day
        rules.push({
            $group: {
                _id: "$dateTask",
                items: {
                    $push: '$$ROOT'
                }
            }
        })

        const logBookPerDay = await LogBook
            .aggregate(rules)
            .sort({ _id: 1 })

        if (!logBook) throw new APIError(errors.serverError)       

        nats.requestOne('userDetail', String(userId), {}, 800, async function(response) {
            // `NATS` is the library.
            if (response.code) {
                res.status(500).send(errors.serverError)
            }
            const responseParseUser = JSON.parse(response)[0]
            const responseParseJabatan = JSON.parse(response)[1]
            const user = JSON.parse(responseParseUser)
            const jabatan = JSON.parse(responseParseJabatan)
            const reporting_date = end_date ? end_date : moment().format('YYYY-MM-DD')
            const layout = reportForm({
                user: user,
                reporting_date: reporting_date,
                jabatan: jabatan,
                logBook: logBook,
                logBookPerDay: logBookPerDay
            })
            const fullName = `${user.first_name}_${user.last_name}`.replace(/[^\w\s]/gi, '')
            const month = req.query.date || moment().format('YYYY')
            const fileName = `LaporanPLD_${month}_${fullName}.pdf`.replace(/[-\s]/g, '_')
            const pdfFile = await generateReport(layout, fileName)

            res.set('Content-disposition', 'attachment; filename=' + fileName)
            res.set('Content-Type', 'attachment')
            res.status(200).send(pdfFile)
        })
    } catch (error) {
        next(error)
    }
}
