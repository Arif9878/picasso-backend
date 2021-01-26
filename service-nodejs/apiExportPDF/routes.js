const express = require('express')

const router = express.Router()

// Import methods
const reportByIdUser = require('./controllers/reportByIdUser')

router.get('/report-by-user/:state/:userId', reportByIdUser)

module.exports = router
