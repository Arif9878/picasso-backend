const sharp = require('sharp')
const moment = require('moment')
const servers_nats = [process.env.NATS_URI]
const nats = require('nats').connect({
    'servers': servers_nats
})

function getUserDetail(Id) {
    return new Promise(resolve => {
        nats.request('userDetail',String(Id), function(resp) {
            resolve(JSON.parse(resp))
            nats.unsubscribe(this._sid)
        })
    })
}

function getListWeekend(start_date, end_date) {
    let list_weekend = []
    for (var d = new Date(start_date); d < new Date(end_date); d.setDate(d.getDate() + 1)) {
        if (d.getDay() === 6 || d.getDay() === 0) {
            list_weekend.push({
                'dateTask':moment(d).format('YYYY-MM-DDTHH:mm:ssZ'),
                'nameTask': 'LIBUR'
            })
        }
    }
    return list_weekend;
}

module.exports = {
    getListWeekend,
    getUserDetail
}
