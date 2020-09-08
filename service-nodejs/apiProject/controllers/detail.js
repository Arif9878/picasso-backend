const {
    errors,
    APIError
} = require('../utils/exceptions')
const Project = require('../models/Project')

// eslint-disable-next-line
module.exports = async (req, res, next) => {
    try {
        const {
            _id
        } = req.params


        if (!_id) throw new APIError(errors.serverError)

        const results = await Project.findById({
            _id: _id
        }).lean()

        if (!results) throw new APIError(errors.serverError)

        res.status(200).json(results)
    } catch (error) {
        next(error)
    }
}

