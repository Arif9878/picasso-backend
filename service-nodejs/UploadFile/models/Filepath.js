const mongoose = require('mongoose')
const Schema = mongoose.Schema
const attributes = require('./Attributes')

const Filepath = new Schema({
    fileType: {
        type: String,
        require: false
    },
    filePath: {
        type: String,
        require: true
    },
    fileURL: {
        type: String,
        require: true
    },
    ...attributes
})

Filepath.index({ filePath: 1 })

module.exports = mongoose.models.Filepath || mongoose.model('Filepath', Filepath)
