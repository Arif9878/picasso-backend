const {
  errors,
  APIError
} = require('../utils/exceptions')
const {
  s3
} = require('../utils/aws')

// Import Model
const LogBook = require('../models/LogBook')
const BlobsFile = require('../models/BlobsFile')
// eslint-disable-next-line
module.exports = async (req, res, next) => {
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
    await LogBook.findByIdAndDelete(_id)
    await BlobsFile.findOneAndRemove({
      logBookId: _id
    })
  
    res.status(200).json({
      code: 'DataDeleted',
      message: 'Data has been successfully deleted',
    })
  } catch (error) {
    const {
      code,
      message,
      data
    } = error

    if (code && message) {
      res.status(code).send({
        code,
        message,
        data,
      })
    } else {
      res.status(404).send(errors.notFound)
    }
  }
}
