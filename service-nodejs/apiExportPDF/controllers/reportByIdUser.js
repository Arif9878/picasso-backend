const { errors, APIError } = require('../utils/exceptions')
const { generateReport, reportForm , holidayType } = require('../utils/generateReport')
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
        const list_weekend = getListWeekend(start_date, dueDate)
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

        // Get logbook
        const logBook = await LogBook
            .aggregate(rules)
            .hint({ nameTask:1 })
            .sort(sort)
        const attendance = await listAttendance(userId, start_date, dueDate)
        const holiday = await listHolidayDate(start_date, dueDate)
        logBook.push(...attendance)
        logBook.push(...list_weekend)
        logBook.push(...holiday)
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

        const detailUser = await getUserDetail(userId)

        if (!detailUser) {
            res.status(500).send(errors.serverError)
        }

        const responseParseUser = detailUser.user
        const tupoksiJabatan = detailUser.tupoksi || []
        const user = JSON.parse(responseParseUser)

        const rulesTupoksi = [
            ...rules,
            {
                $group: {
                    _id: "$tupoksiJabatanId",
                    name : { $first: '$tupoksiJabatanName' },
                    items: {
                        $push: '$$ROOT'
                    },
                    count: { $sum: 1 }
                }
            }
        ]

        // Get logbook per tupoksi
        const resultsTupoksi = await LogBook
                .aggregate(rulesTupoksi)
                .sort({ _id: 1 })
        const indexDiluarTupoksi = resultsTupoksi.findIndex((element, index) => {
            if (element._id === process.env.TUPOKSI_DILUAR_TUGAS) {
                return true
            }
        })
        let logBookByTupoksi = []
        for (const tupoksi of tupoksiJabatan) {
            for (const item of resultsTupoksi) {
                if (tupoksi === item.name) {
                    logBookByTupoksi.push(item)
                }
            }
        }
        // Di luar tupoksi
        if (indexDiluarTupoksi != -1) {
            logBookByTupoksi.push(resultsTupoksi[indexDiluarTupoksi])
        }

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
            for (const eachDay of logBookByTupoksi) {
                for (const items of eachDay.items) {
                    const results = await axios.get(items.blobTaskURL)
                    items['blobsEvidence'] = results.data
                }
            }
        } 

        if (!logBook) throw new APIError(errors.serverError)       

        const reporting_date = end_date ? end_date : moment().format('YYYY-MM-DD')
        const layout = reportForm({
            user: user,
            reporting_date: reporting_date,
            jabatan: tupoksiJabatan,
            logBook: logBook,
            logBookPerDay: logBookPerDay,
            logBookTupoksi: logBookByTupoksi
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
