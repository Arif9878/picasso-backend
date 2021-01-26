const {
    errors,
} = require('../utils/exceptions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')
const moment = require('moment')
moment.locale('id')
// Import Model
const Attendance = require('../models/Attendance')

module.exports = async (req, res) => { // eslint-disable-line
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        const session = req.user

        const start = moment().format("YYYY/MM/DD")

        const end = moment().format("YYYY/MM/DD")

        const rules = [{
            $match: {
                'createdBy.email': session.email,
                startDate: {
                    $gte: new Date(`${start} 00:00:00`),
                    $lt: new Date(`${end} 23:59:59`)
                }
            },
        }]
        const checkUserCheckin = await Attendance.aggregate(rules)

        if (checkUserCheckin.length >= 1) {
            res.status(201).send({
                isCheckin: true,
            })
        } else {
            res.status(201).send({
                isCheckin: false,
            })
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
