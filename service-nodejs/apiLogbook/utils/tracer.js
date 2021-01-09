const ZIPKIN_URL = process.env.ZIPKIN_URL || 'http://127.0.0.1:9411/api/v2/spans'
const { Tracer, BatchRecorder, jsonEncoder: { JSON_V2 } } = require('zipkin')
const CLSContext = require('zipkin-context-cls');  
const { HttpLogger } = require('zipkin-transport-http');

// tracing
const ctxImpl = new CLSContext('zipkin')
const recorder = new  BatchRecorder({
  logger: new HttpLogger({
    endpoint: ZIPKIN_URL,
    jsonEncoder: JSON_V2
  })
})
const localServiceName = 'logbook-api'
const tracer = new Tracer({ctxImpl, recorder, localServiceName})

module.exports = {
    tracer
}
