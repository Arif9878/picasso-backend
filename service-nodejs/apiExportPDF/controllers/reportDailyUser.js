const { errors, APIError } = require('../utils/exceptions')
const { generateReport, holidayType } = require('../utils/generateReport')
const { reportFormDaily } = require('../utils/generateReportDaily')
const { getListWeekend, getUserDetail } = require('../utils/functions')
const { listAttendance, listHolidayDate } = require('../utils/listOtherReport')
const { tracer } = require('../utils/tracer')
const axios = require('axios')
const opentracing = require('opentracing')

const LogBook = require('../models/LogBook')
const moment = require('moment')

// eslint-disable-next-line
module.exports = async (req, res) => {
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        let sort = {
            dateTask: 1,
        }
        const {
            userId,
            state
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
                    'tupoksiJabatanId': { '$ifNull': ['$tupoksiJabatanId', ''] },
                    'tupoksiJabatanName': { '$ifNull': ['$tupoksiJabatanName', ''] },
                    'evidenceTaskPath': '$evidenceTask.filePath',
                    'evidenceTaskURL': '$evidenceTask.fileURL',
                    'evidenceBlob': '$evidenceTask.fileBlob',
                    'documentTaskPath': '$documentTask.filePath',
                    'documentTaskURL': '$documentTask.fileURL',
                    'blobTaskURL': '$blobTask.fileURL'
                }
            }
        ]

        // Get logbook, list_weekend, attendance, holiday, detailUser
        const [logBook, list_weekend, attendance, holiday, detailUser] = await Promise.all([
            LogBook.aggregate(rules).sort(sort),
            getListWeekend(start_date, dueDate),
            listAttendance(userId, start_date, dueDate),
            listHolidayDate(start_date, dueDate),
            getUserDetail(userId),
        ])

        logBook.push(...attendance, ...list_weekend, ...holiday)
        logBook.sort(function (a, b) {
            return new Date(a.dateTask) - new Date(b.dateTask)
        })
       logBook.filter((a, b) => {
            index = b+1
            if (logBook[index] === undefined) return
            if (moment(a.dateTask).isSame(logBook[b+1].dateTask, 'day')) {
                if (logBook[b+1].nameTask === 'LIBUR' || holidayType.includes(logBook[b+1].type)) {
                    logBook.splice(index,1)
                } else if (a.nameTask === 'LIBUR' || holidayType.includes(a.type)) {
                    logBook.splice(logBook.indexOf(a),1)
                }
            }
        })

        if (!detailUser) {
            res.status(500).send(errors.serverError)
        }

        const responseParseUser = detailUser.user
        const tupoksiJabatan = detailUser.tupoksi || []
        const user = JSON.parse(responseParseUser)

        // Get logbook per Day
        rules.push({
            $group: {
                _id: "$dateTask",
                items: {
                    $push: '$$ROOT'
                }
            }
        })
        let logBookPerDay = []
        if (state != 'view') {
            logBookPerDay = await LogBook
                .aggregate(rules)
                .sort({ _id: 1 })

            for (const eachDay of logBookPerDay) {
                for (const items of eachDay.items) {
                    const results = await axios.get(items.blobTaskURL)
                    items['blobsEvidence'] = results.data
                }
            }
        } 

        if (!logBook) throw new APIError(errors.serverError)       

        const reporting_date = end_date ? end_date : moment().format('YYYY-MM-DD')
        const layout = reportFormDaily({
            user: user,
            reporting_date: reporting_date,
            jabatan: tupoksiJabatan,
            logBook: logBook,
            logBookPerDay: logBookPerDay
        })
        const fullName = `${user.first_name}_${user.last_name}`.replace(/[^\w\s]/gi, '')
        const month = req.query.date || moment().format('YYYY')
        const fileName = `LaporanPLD_${month}_${fullName}.pdf`.replace(/[-\s]/g, '_')
        const pdfFile = await generateReport(layout, fileName)
        if (state != 'view') {
            res.set('Content-disposition', 'attachment; filename=' + fileName)
            res.set('Content-Type', 'attachment')
            res.status(200).send(pdfFile)
        } else {
            const pdfBlob = 'data:application/pdf;base64,' + pdfFile.toString('base64')
            res.set('content-type', 'application/pdf')
            res.status(200).send(pdfBlob)
        }
        tracer.inject(span, "http_headers", req.headers)
        span.setTag(opentracing.Tags.HTTP_STATUS_CODE, 200)
    } catch (error) {
        const { code, message, data } = error

        span.setTag(opentracing.Tags.HTTP_STATUS_CODE,code)
        if (code && message) {
            res.status(code).send({ code, message, data })
        } else {
            res.status(500).send(errors.serverError)
        }
    }
    span.finish()
}
