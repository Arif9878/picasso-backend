const jwt = require('jsonwebtoken')
const { errors, APIError } = require('../utils/exceptions')

module.exports = async (req, res, next) => { // eslint-disable-line
    try {
        let token
        const { authorization } = req.headers
        if (req.headers.authorization && authorization.split(' ')[1]) token = authorization.split(' ')[1]        
        if (!token) throw new APIError(errors.tokenNotFound)
        const authenticated = await jwt.verify(token, process.env.SECRET_KEY)
        if (!authenticated) throw new APIError(errors.wrongCredentials)

        req.user = authenticated

        next()
    } catch (error) {
        const { name, code, message, data } = error
        if (name === 'TokenExpiredError') {
            res.status(401).send(errors.tokenExpired)
        } else if (code && message) {
            res.status(code).send({ code, message, data })
        } else {
            res.status(500).send(errors.serverError)
        }
    }
}
