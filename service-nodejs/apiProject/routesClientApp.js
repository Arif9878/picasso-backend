const express = require('express')

const router = express.Router()
// Import methods
const clientAppListProject = require('./controllersClient/clientAppListProject')

router.get('/project/app/', clientAppListProject)

module.exports = router
