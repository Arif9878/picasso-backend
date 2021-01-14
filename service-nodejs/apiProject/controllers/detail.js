const {
    errors,
    APIError
} = require('../utils/exceptions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')
const Project = require('../models/Project')

// eslint-disable-next-line
module.exports = async (req, res, next) => {
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        const {
            _id
        } = req.params


        if (!_id) throw new APIError(errors.serverError)

        const results = await Project.findById({
            _id: _id
        }).lean()

        if (!results) throw new APIError(errors.serverError)

        res.status(200).json(results)
        tracer.inject(span, "http_headers", req.headers)
        span.setTag(opentracing.Tags.HTTP_STATUS_CODE, 200)
    } catch (error) {
        const { code } = error
        span.setTag(opentracing.Tags.HTTP_STATUS_CODE, code)
        next(error)
    }
    span.finish()
}

