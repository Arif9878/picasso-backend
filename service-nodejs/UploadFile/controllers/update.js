const { errors } = require('../utils/exceptions')
const { onUpdated } = require('../utils/session')
const { s3 } = require('../utils/aws')
// Import Model
const Filepath = require('../models/Filepath')

module.exports = async (req, res) => { // eslint-disable-line
    try {
        const { id: _id } = req.params
        const session = req.user

        const {
            filePath = null,
            fileURL = null
        } = req.body

        const data = {
            filePath,
            fileURL,
            ...onUpdated(session)
        }

        await Filepath.findOneAndUpdate({ _id }, data)

        res.status(201).send({
            message: 'Update data successfull',
            data,
        })
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
