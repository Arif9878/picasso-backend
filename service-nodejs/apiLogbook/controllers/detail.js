const {
    errors,
    APIError
} = require('../utils/exceptions')
const LogBook = require('../models/LogBook')

// eslint-disable-next-line
module.exports = async (req, res, next) => {
    try {
        const {
            _id
        } = req.params

        if (!_id) throw new APIError(errors.serverError)
       
        const results = await LogBook.findById({
            _id: _id
        }).lean()

        if (!results) throw new APIError(errors.serverError)

        res.status(200).json(results)
    } catch (error) {
        next(error) 
    }
}

