const mongoose = require('mongoose')
const Schema = mongoose.Schema
const attributes = require('./Attributes')

const LogBook = new Schema({
    dateTask: {
        type: Date,
        required: false,
        default: null
    },
    tupoksiJabatanId: {
      type: String,
      required: false,
      default: null
    },
    tupoksiJabatanName: {
      type: String,
      required: false,
      default: null
    },
    projectId: {
      type: String,
      required: true,
      default: null
    },
    projectName: {
      type: String,
      required: true,
      default: null
    },
    nameTask: {
        type: String,
        required: true,
        default: null
    },
    difficultyTask: {
        type: Number,
        required: false,
        default: null
    },
    evidenceTask: {
        filePath: {
            type: String,
            required: false,
            default: null,
        },
        fileURL: {
            type: String,
            required: false,
            default: null,
        }
    },
    documentTask: {
        filePath: {
            type: String,
            required: false,
            default: null,
        },
        fileURL: {
            type: String,
            required: false,
            default: null,
        },
    },
    blobTask: {
        filePath: {
            type: String,
            required: false,
            default: null,
        },
        fileURL: {
            type: String,
            required: false,
            default: null,
        },
    },
    isDocumentLink: {
        type: Boolean,
        required: false,
        default: false
    },
    isMainTask: {
        type: Boolean,
        required: false,
        default: false
    },
    workPlace: {
        type: String,
        required: false,
        default: null
    },
    organizerTask: {
        type: String,
        required: false,
        default: null
    },
    otherInformation: {
        type: String,
        required: false,
        default: null
    },
    ...attributes
})

LogBook.index({
    dateTask: 1,
    nameTask: 1,
    projectId: 1,
    projectName: 1
})

module.exports = mongoose.models.LogBook || mongoose.model('LogBook', LogBook)
