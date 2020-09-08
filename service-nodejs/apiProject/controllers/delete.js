const { errors, APIError } = require('../utils/exceptions')
// Import Model
const Project = require('../models/Project')

// eslint-disable-next-line
module.exports = async (req, res, next) => {
  try {
    const { _id } = req.params

    if (!_id) throw new APIError(errors.notFound)

    await Project.findByIdAndDelete(_id)

    res.status(200).json({
      code: 'DataDeleted',
      message: 'Data has been successfully deleted',
    })
  } catch (error) {
    next(error)
  }
}
