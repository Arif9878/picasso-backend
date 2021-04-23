const express = require('express')
const {
    formCheckin,
    formCheckout
} = require('./models/Validator')

const router = express.Router()

// Import methods
const clientAppCheckin = require('./controllersClient/clientAppCheckin')
const clientAppCheckout = require('./controllersClient/clientAppCheckout')
const clientAppListAttendance = require('./controllersClient/clientAppListAttendance')

router.post('/attendance/app/checkin', formCheckin(), clientAppCheckin)
router.post('/attendance/app/checkout', formCheckout(), clientAppCheckout)
router.get('/attendance/app/list', clientAppListAttendance)

module.exports = router
