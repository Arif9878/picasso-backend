const express = require('express')

const router = express.Router()
// Import methods
const create = require('./controllers/create')
const update = require('./controllers/update')
const detailBlobImage = require('./controllers/detailBlobImage')
const detailFile = require('./controllers/detailFile')

router.post('/', create)
router.put('/:id', update)
router.get('/image-blob/:name', detailBlobImage)
router.get('/:path/:name', detailFile)

module.exports = router
