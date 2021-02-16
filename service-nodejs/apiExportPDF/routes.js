const express = require('express')

const router = express.Router()

// Import methods
const reportByIdUser = require('./controllers/reportByIdUser')
const reportDailyUser = require('./controllers/reportDailyUser')

router.get('/report-by-user/:state/:userId', reportByIdUser)
router.get('/report-by-user/daily/:state/:userId', reportDailyUser)

module.exports = router
