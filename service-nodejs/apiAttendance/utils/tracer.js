const { initTracer } = require('jaeger-client')

//set up our tracer
const config = {
  serviceName: 'attendace-api',
  reporter: {
    logSpans: true,
    collectorEndpoint: process.env.JAEGER_COLLECTTOR_END_POINT,
  },
  sampler: {
    type: 'const',
    param: 1
  }
}
const options = {
  tags: {
    'attendace-api': '1.0.0'
  }
}
const tracer = initTracer(config, options);

module.exports = { 
  tracer
}
