
const { errors } = require('../utils/exceptions')
const { onUpdated } = require('../utils/session')
const { s3 } = require('../utils/aws')

// Import Model
const Filepath = require('../models/Filepath')

module.exports = async (req, res) => { // eslint-disable-line
    try {
        const { id: _id } = req.params

        const file = await Filepath.findById({ _id })

        var deleteParam = {
            Bucket: process.env.AWS_S3_BUCKET,
            Delete: {
                Objects: [
                    {Key: file.filePath}
                ]
            }
        };
        s3.deleteObjects(deleteParam, function(err, data) {
          if (err) {
              throw new APIError(errors.serverError)
          }
          if (data) {
            res.status(201).send({
                message: 'Delete data successfull',
                data,
            })
          }
        });

    } catch (error) {
        const { code, message, data } = error

        if (code && message) {
            res.status(code).send({
                code,
                message,
                data,
            })
        } else {
            res.status(500).send(errors.serverError)
        }
    }
}
