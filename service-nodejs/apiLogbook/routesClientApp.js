const express = require('express')
const {
    form
} = require('./models/Validator')

const router = express.Router()
// Import methods
const createClientApp = require('./controllersClient/createClientApp')

router.post('/logbook/app', form(), createClientApp)

module.exports = router
