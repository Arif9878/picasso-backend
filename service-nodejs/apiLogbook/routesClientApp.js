const express = require('express')
const {
    form
} = require('./models/Validator')

const router = express.Router()
// Import methods
const clientAppCreateLogbook = require('./controllersClient/clientAppCreateLogbook')
const clientAppListLogbook = require('./controllersClient/clientAppListLogbook')

router.post('/logbook/app', form(), clientAppCreateLogbook)
router.get('/logbook/app/list/batch/', clientAppListLogbook)

module.exports = router
