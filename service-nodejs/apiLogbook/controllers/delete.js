const { errors, APIError } = require('../utils/exceptions')
const { s3 } = require('../utils/aws')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')

// Import Model
const LogBook = require('../models/LogBook')

// eslint-disable-next-line
module.exports = async (req, res) => {
  const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
  const span = tracer.startSpan(req.originalUrl, {
      childOf: parentSpan,
  })
  try {
    const { _id } = req.params

    if (!_id) throw new APIError(errors.notFound)

    const results = await LogBook.findById({
      _id: _id
    }).lean()

    const deleteParamEvidence = {
      Bucket: process.env.AWS_S3_BUCKET,
      Delete: {
        Objects: [{
          Key: results.evidenceTask.filePath
        }]
      }
    }

    await s3.deleteObjects(deleteParamEvidence, function (err, data) {
      if (err) {
        console.error(err)
      }
    })

    if (results.documentTask.filePath) {
      const deleteParamDocument = {
        Bucket: process.env.AWS_S3_BUCKET,
        Delete: {
          Objects: [{
            Key: results.documentTask.filePath
          }]
        }
      }

      await s3.deleteObjects(deleteParamDocument, function (err, data) {
        if (err) {
          console.error(err)
        }
      })
    }
  
    if (results.blobTask.filePath) {
      const deleteParamBlob = {
        Bucket: process.env.AWS_S3_BUCKET,
        Delete: {
          Objects: [{
            Key: results.blobTask.filePath
          }]
        }
      }

      await s3.deleteObjects(deleteParamBlob, function (err, data) {
        if (err) {
          console.error(err)
        }
      })
    }
  
    await LogBook.findByIdAndDelete(_id)
  
    res.status(200).json({
      code: 'DataDeleted',
      message: 'Data has been successfully deleted',
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
