const mongoose = require('mongoose')
const Schema = mongoose.Schema
const attributes = require('./Attributes')
const {
    attendanceConnection
} = require('../utils/connections')

const Attendance = new Schema({
    startDate: {
        type: Date,
        required: true,
        default: null
    },
    endDate: {
        type: Date,
        required: false,
        default: null
    },
    officeHours: {
        type: Number,
        required: false,
        default: 0
    },
    location: {
        type: String,
        required: true,
        default: null
    },
    message: {
      type: String,
      required: false,
      default: null
    },
    note: {
        type: String,
        required: false,
        default: null
    },
    ...attributes
})

Attendance.index({
    location: 1
})

// module.exports = mongoose.models.Attendance || mongoose.model('Attendance', Attendance)
const attendanceModel = attendanceConnection.model('Attendance', Attendance)

module.exports = attendanceModel