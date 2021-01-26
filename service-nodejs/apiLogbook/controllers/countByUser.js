const { errors, APIError } = require('../utils/exceptions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')
const LogBook = require('../models/LogBook')

// eslint-disable-next-line
module.exports = async (req, res) => {
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        const {
            _id
        } = req.params

        if (!_id) throw new APIError(errors.serverError)

        const date = new Date(),
            year = date.getFullYear(),
            month = date.getMonth()
        const firstMonth = new Date(year, month, 1)
        const lastMonth = new Date(year, month + 1, 0)

        const rules = [{
            '$match': {
                'createdBy._id': _id,
                'dateTask': {
                    '$gte': firstMonth,
                    '$lt': lastMonth
                }
            }
        }, {
            '$group': {
                '_id': 0,
                'total': {
                    '$sum': 1
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'total': 1
            }
        }]

        const results = await LogBook
            .aggregate(rules)

        if (!results) throw new APIError(errors.serverError)

        res.status(200).json(results)
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
