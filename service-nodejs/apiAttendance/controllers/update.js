const {
    errors,
    APIError
} = require('../utils/exceptions')
const {
    onUpdated
} = require('../utils/session')
const {
    validationResult
} = require('express-validator')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')
// Import Model
const Attendance = require('../models/Attendance')

module.exports = async (req, res) => { // eslint-disable-line
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        const session = req.user
        const errors = validationResult(req)
        if (!errors.isEmpty()) {
            res.status(422).json({
                code: 422,
                errors: errors.array(),
            })
            return
        }
        const { _id } = req.params
        if (!_id) throw new APIError(errors.notFound)

        const {
            checkinAt = null,
            location = null,
            message = null,
        } = req.body

        const data = {
          checkinAt,
          location,
          message,
            ...onUpdated(session)
        }

        const results = await Attendance.findByIdAndUpdate(_id, data)

        await res.status(201).send({
            message: 'Update data successfull',
            data: results,
        })

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
