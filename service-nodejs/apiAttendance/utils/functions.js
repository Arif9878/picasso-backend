const moment = require("moment")

function calculateHours(startDate, endDate) {
    const start_date = moment(startDate, 'YYYY-MM-DD HH:mm:ss')
    const end_date = moment(endDate, 'YYYY-MM-DD HH:mm:ss')
    const duration = moment.duration(end_date.diff(start_date))
    const hours = duration.asHours()
    return hours.toFixed(2)
}

const arrayMood = ['worst', 'sad', 'neutral', 'good', 'excellent']

module.exports = {
    calculateHours,
    arrayMood
}
