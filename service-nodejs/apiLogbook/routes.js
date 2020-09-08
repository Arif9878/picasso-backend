const express = require('express')
const {
    form
} = require('./models/Validator')

const router = express.Router()
// Import methods
const create = require('./controllers/create')
const update = require('./controllers/update')
const deleted = require('./controllers/delete')
const list = require('./controllers/list')
const detail = require('./controllers/detail')
const reportByIdUser = require('./controllers/reportByIdUser')

router.post('/', form(), create)
router.put('/:_id', form(), update)
router.delete('/:_id', deleted)
router.get('/:_id', detail)
router.get('/', list)
router.get('/report-by-user/:userId', reportByIdUser)

module.exports = router
