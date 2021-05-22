const jwt = require('jsonwebtoken')
const { errors, APIError } = require('../utils/exceptions')

module.exports = async (req, res, next) => { // eslint-disable-line
    try {
        let token
        const { authorization } = req.headers
        if (req.headers.authorization && authorization.split(' ')[1]) token = authorization.split(' ')[1]        
        if (!token) throw new APIError(errors.tokenNotFound)
        const authenticated = jwt.decode(token)
        if (!authenticated) throw new APIError(errors.wrongCredentials)

        req.client_app = authenticated

        next()
    } catch (error) {
        const { name } = error
        if (name === 'TokenExpiredError') {
            res.status(401).send(errors.tokenExpired)
        } else {
            res.status(500).send(errors.serverError)
        }
    }
}
