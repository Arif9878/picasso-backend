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

        const date = new Date(),
            year = date.getFullYear(),
            month = date.getMonth()
        const firstMonth = new Date(year, month, 1)
        const lastMonth = new Date(year, month + 1, 0)

        const rules = [{
            '$match': {
                'createdBy._id': _id,
                'dateTask': {
                    '$gte': firstMonth,
                    '$lt': lastMonth
                }
            }
        }, {
            '$group': {
                '_id': 0,
                'total': {
                    '$sum': 1
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'total': 1
            }
        }]

        const results = await LogBook
            .aggregate(rules)

        if (!results) throw new APIError(errors.serverError)

        res.status(200).json(results)
    } catch (error) {
        next(error)
    }
}
