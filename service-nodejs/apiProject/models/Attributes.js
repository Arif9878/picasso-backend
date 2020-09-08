const mongoose = require('mongoose')
const mongooseLogs = require('mongoose-activitylogs')
const moment = require('moment')
moment.locale('id')

module.exports = {
    createdBy: {
        _id: {
            type: String,
            required: false,
            default: null,
        },
        email: {
            type: String,
            required: false,
            default: null,
        },
        username: {
            type: String,
            required: false,
            default: null,
        },
    },
    createdAt: {
        type: Date,
        default: new Date(moment().format()),
    },
    updatedBy: {
        _id: {
            type: String,
            required: false,
            default: null,
        },
        email: {
            type: String,
            required: false,
            default: null,
        },
        username: {
            type: String,
            required: false,
            default: null,
        },
    },
    updatedAt: {
        type: Date,
        required: false,
        default: null,
    },
}
