const moment = require("moment")
const redis = require('redis')
const redisClient = redis.createClient({
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT
})

function getKeyRedis(key) {
    return new Promise(resolve => {
        redisClient.get(key, function(err, data) {
            if (err) throw new APIError(errors.serverError)
            resolve(JSON.parse(data))
        })
    })
}


function calculateHours(startDate, endDate) {
    const start_date = moment(startDate, 'YYYY-MM-DD HH:mm:ss')
    const end_date = moment(endDate, 'YYYY-MM-DD HH:mm:ss')
    const duration = moment.duration(end_date.diff(start_date))
    const hours = duration.asHours()
    return hours.toFixed(2)
}

module.exports = {
    calculateHours,
    getKeyRedis
}
