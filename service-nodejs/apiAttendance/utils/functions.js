const moment = require("moment")
const servers_nats = [process.env.NATS_URI]
const nats = require('nats').connect({
    'servers': servers_nats
})

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

function getUserDetail(Id) {
    return new Promise(resolve => {
        nats.request('userDetail',String(Id), function(resp) {
            resolve(JSON.parse(resp))
            nats.unsubscribe(this._sid)
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

const arrayMood = ['worst', 'sad', 'neutral', 'good', 'excellent']

module.exports = {
    calculateHours,
    arrayMood,
    getUserDetail,
    getKeyRedis
}
