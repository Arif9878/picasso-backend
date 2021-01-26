const mongoose = require('mongoose')
const Schema = mongoose.Schema
const {
    holidaydateConnection
} = require('../utils/connections')

const HolidayDate = new Schema({
    holiday_date: {
        type: Date,
        required: true,
        default: null
    },
    holiday_type: {
        type: String,
        required: false,
        default: null
    },
    holiday_name: {
        type: String,
        required: false,
        default: null
    },
}, { collection: 'holidaydate'})

const holidayDateModel = holidaydateConnection.model('holidaydate', HolidayDate)

module.exports = holidayDateModel