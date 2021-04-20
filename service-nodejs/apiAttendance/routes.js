const express = require('express')
const {
    formCheckin,
    formCheckout
} = require('./models/Validator')

const router = express.Router()
// Import methods
const checkin = require('./controllers/checkin')
const checkinClientApp = require('./controllers/checkinClientApp')
const checkout = require('./controllers/checkout')
const isCheckin = require('./controllers/isCheckin')
const isCheckout = require('./controllers/isCheckout')
const update = require('./controllers/update')
const deleted = require('./controllers/delete')
const list = require('./controllers/list')
const detail = require('./controllers/detail')

router.post('/checkin', formCheckin(), checkin)
router.post('/client/checkin', formCheckin(), checkinClientApp)
router.post('/checkout', formCheckout(), checkout)
router.put('/:_id', formCheckin(), update)
router.delete('/:_id', deleted)
router.get('/:_id', detail)
router.get('/is/checkin', isCheckin)
router.get('/is/checkout', isCheckout)
router.get('/', list)

module.exports = router
