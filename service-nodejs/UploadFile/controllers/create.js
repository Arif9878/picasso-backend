const { errors, APIError } = require('../utils/exceptions')
const { onCreated } = require('../utils/session')
const { getRandomString } = require('../utils/randomString')

// Import Model
const Filepath = require('../models/Filepath')
const { s3 } = require('../utils/aws')

module.exports = async (req, res) => { // eslint-disable-line
    try {
        const session = req.user
        if (!req.files || Object.keys(req.files).length === 0) throw new APIError(errors.serverError)

        const {
          fileType = null
        } = req.body

        const fileName = req.files.file.name;
        const file_ext = fileName.substr((Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1)
        const newFileName = getRandomString(32) + '.' + file_ext;
        let params = {
            Bucket: process.env.AWS_S3_BUCKET,
            Body : req.files.file.data,
            Key: fileType + "/" + Date.now() + "/" + newFileName
        }

        await s3.upload(params, async function (err, data) {
            //handle error
            if (err) {
                throw new APIError(errors.serverError)
            }
            //handle success
            const fileData = {
                fileType: fileType,
                filePath: data.key,
                fileURL: data.Location,
                ...onCreated(session)
            }

            const results = await Filepath.create(fileData)

            await res.status(201).send({
                message: 'Input data successfull',
                data: results
            })
        })

    } catch (error) {
        const { code, message, data } = error
        console.log(error)

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
