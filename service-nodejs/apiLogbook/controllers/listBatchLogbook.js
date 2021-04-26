const { errors } = require('../utils/exceptions')
const { tracer } = require('../utils/tracer')
const { getKeyRedis } = require('../utils/functions')
const opentracing = require('opentracing')

// eslint-disable-next-line
module.exports = async (req, res) => {
  const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
  const span = tracer.startSpan(req.originalUrl, { childOf: parentSpan })

  try {
    // Get request params
    const session = req.user

    // get from redis
    const getDataRedis = await getKeyRedis(session.user_id, 'logbooks')

    // delete key created by
    const logBook = await getDataRedis.map(({createdById, ...rest}) => rest) || []

    res.status(200).json(logBook)

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
