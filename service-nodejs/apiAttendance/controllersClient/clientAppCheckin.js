const {
    errors,
    APIError
} = require('../utils/exceptions')
const {
    validationResult
} = require('express-validator')
const {
    onClientApp,
    onCreatedClientApp
} = require('../utils/session')
const { tracer } = require('../utils/tracer')
const { getKeyRedis, getUserDetail } = require('../utils/functions')

const opentracing = require('opentracing')
const moment = require('moment')
moment.locale('id')

// Import Model
const Attendance = require('../models/Attendance')

module.exports = async (req, res) => { // eslint-disable-line
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, { childOf: parentSpan })
    try {
        if (!req.body.createdBy) throw new APIError({
            code: 401,
            message: 'Token not found',
        })

        // get from redis
        const getDataRedisUser = await getKeyRedis('users')
        const resp = await getDataRedisUser.map((val) => { 
            if (val.id === req.body.createdBy) return val
        })
        let user = resp[0]

        // get from message broker
        if (!user) {
            const resp = await getUserDetail(req.body.createdBy)
            user = JSON.parse(resp.user)
        }

        const session_client = req.client_app

        const errors = validationResult(req)
        if (!errors.isEmpty()) {
            res.status(422).json({
                code: 422,
                errors: errors.array(),
            })
            return
        }
        const {
            date = null,
            location = null,
            message = null,
            note = null
        } = req.body

        const start = moment().format("YYYY/MM/DD")

        const end = moment().format("YYYY/MM/DD")

        if (moment().isSame(date, 'day') === false) throw new APIError({
            code: 422,
            message: 'Tanggal checkin tidak sesuai dengan hari ini.',
        })

        const rules = [{
            $match: {
                'createdBy.email': user.email,
                startDate: {
                    $gte: new Date(`${start} 00:00:00`),
                    $lt: new Date(`${end} 23:59:59`)
                }
            },
        }]
        const checkUser = await Attendance.aggregate(rules)

        if (checkUser.length >= 1) throw new APIError({
            code: 422,
            message: 'Sudah melakukan checkin',
        })

        const data = {
            startDate: date,
            location,
            message,
            note,
            ...onCreatedClientApp(user),
            ...onClientApp(session_client)
        }

        const results = await Attendance.create(data)

        res.status(201).send({
            message: 'Input data successfull',
            data: results,
        })

        tracer.inject(span, "http_headers", req.headers)
        span.setTag(opentracing.Tags.HTTP_STATUS_CODE, 200)
    } catch (error) {
        const { code, message, data } = error
        span.setTag(opentracing.Tags.HTTP_STATUS_CODE,code)

        if (code && message) {
            res.status(code).send({ code, message, data })
        } else {
            res.status(500).send(errors.serverError)
        }
    }
    span.finish()
}
