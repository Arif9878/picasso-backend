const mongoose = require('mongoose')
const Schema = mongoose.Schema
const {
    logBookConnection
} = require('../utils/connections')

const BlobsFile = new Schema({
    logBookId: mongoose.Schema.Types.ObjectId,
    dateTask: {
        type: Date,
        required: false,
        default: null
    },
    blob: {
        type: String,
        required: false,
        default: null
    }
})

BlobsFile.index({
    _id: 1,
    dateTask: 1,
    logBookId: 1
})

const blobsFileModel = logBookConnection.model('BlobsFile', BlobsFile)

module.exports = blobsFileModel