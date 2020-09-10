const mongoose = require('mongoose')
const Schema = mongoose.Schema

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
    logBookId: 1,
    blob: 1
})

module.exports = mongoose.models.BlobsFile || mongoose.model('BlobsFile', BlobsFile)
