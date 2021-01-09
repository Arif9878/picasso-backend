const {
    errors,
    APIError
} = require('../utils/exceptions')
const mongoose = require('mongoose')
const { 
    generateReport,
    reportForm ,
    holidayType
} = require('../utils/generateReport')
const {
    getListWeekend,
} = require('../utils/functions')
const {
    listAttendance,
    listHolidayDate
} = require('../utils/listOtherReport')
const LogBook = require('../models/LogBook')
const BlobsFile = require('../models/BlobsFile')
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
            // {
            //     '$lookup': {
            //         'from': 'blobsfiles',
            //         'localField': '_id',
            //         'foreignField': 'logBookId',
            //         'as': 'blobsEvidence'
            //     }
            // },
            // {
            //     '$unwind': {
            //         'path': '$blobsEvidence',
            //         'includeArrayIndex': 'arrayIndex'
            //     }
            // },
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
                    'documentTaskURL': '$documentTask.fileURL'
                    // 'blobsEvidence': '$blobsEvidence.blob'
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
                    const results = await BlobsFile.findOne({ logBookId: mongoose.Types.ObjectId(items._id) }).lean()
                    items['blobsEvidence'] = results.blob
                }
            }
        } 
             
        if (!logBook) throw new APIError(errors.serverError)       

        const report = []
        // `NATS` is the library.
        const sid = nats.request('userDetail', String(userId), (response) => {
            report.push(JSON.parse(response)[0])
            report.push(JSON.parse(response)[1])
        })
        setTimeout(async () => {
            nats.unsubscribe(sid)
            if (!report[0]) {
                res.status(500).send(errors.serverError)
            }
            const responseParseUser = report[0]
            const responseParseJabatan = report[1]
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
            if (state != 'view') {
                res.set('Content-disposition', 'attachment; filename=' + fileName)
                res.set('Content-Type', 'attachment')
                res.status(200).send(pdfFile)
            } else {
                const pdfBlob = 'data:application/pdf;base64,' + pdfFile.toString('base64')
                res.set('content-type', 'application/pdf')
                res.status(200).send(pdfBlob)
            }
        }, 500)
    } catch (error) {
        next(error)
    }
}
