const express = require('express')
const {
    formCheckin,
    formCheckout
} = require('./models/Validator')

const router = express.Router()

// Import methods
const checkinClientApp = require('./controllersClient/checkinClientApp')
const checkoutClientApp = require('./controllersClient/checkoutClientApp')
const listClientApp = require('./controllersClient/listAttendanceClientApp')

router.post('/attendance/app/checkin', formCheckin(), checkinClientApp)
router.post('/attendance/app/checkout', formCheckout(), checkoutClientApp)
router.post('/attendance/app/list', listClientApp)

module.exports = router
