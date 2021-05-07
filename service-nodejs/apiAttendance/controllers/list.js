const mongoose = require('mongoose')
const { errors, APIError } = require('../utils/exceptions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')
const Attendance = require('../models/Attendance')
const moment = require('moment')
moment.locale('id')

// eslint-disable-next-line
module.exports = async (req, res) => {
  const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
  const span = tracer.startSpan(req.originalUrl, {
      childOf: parentSpan,
  })
  try {
    // Get request params
    let sort = {
      startDate: 1,
    }
    const page = parseInt(req.query.page) || 1
    const pageSize = parseInt(req.query.pageSize) || 10
    const skip = (page - 1) * pageSize
    const {
      search,
      date,
      sort: _sort
    } = req.query
    let start, end

    const rules = [
      {
        '$project': {
          'startDate': 1,
          'endDate': 1,
          'officeHours': 1,
          'location': 1,
          'message': 1,
          'note': 1,
          'mood': { '$ifNull': ['$mood', ''] },
          'fullname': '$createdBy.fullname',
          'email': '$createdBy.email',
          'username': '$createdBy.username',
          'divisi': '$createdBy.divisi',
          'jabatan': '$createdBy.jabatan'
        }
      }
    ]

    start = moment().format("YYYY/MM/DD")
    end = moment().format("YYYY/MM/DD")

    if (date) {
      start = moment(date).format("YYYY/MM/DD")
      end = moment(date).format("YYYY/MM/DD")

      rules.push({
        '$match': {
          'startDate': {
            $gte: new Date(`${start} 00:00:00`),
            $lt: new Date(`${end} 23:59:59`)
          }
        },
      })
    } else {
      rules.push({
        $match: {
          startDate: {
            $gte: new Date(`${start} 00:00:00`),
            $lt: new Date(`${end} 23:59:59`)
          }
        },
      })
    }

    if (_sort) {
      const __sort = _sort.split(',')
      sort = {
        [__sort[0]]: __sort[1] === 'asc' ? 1 : -1,
      }
    }

    if (search) {
      const terms = new RegExp(search, 'i')

      rules.push({
        '$match': {
          'location': {
            '$regex': terms,
          },
        },
      })
    }

    // Get page count
    const filtered = await Attendance.aggregate([
      ...rules,
      {
        '$group': { _id: null, rows: { '$sum': 1 } },
      },
      {
        '$project': {
          rows: 1,
        },
      },
    ])

    const totalPage = Math.ceil((filtered.length > 0 ? filtered[0].rows : 0) / pageSize)

    // Get results
    const results = await Attendance
      .aggregate(rules)
      .sort(sort)
      .skip(skip)
      .limit(pageSize)

    res.status(200).json({
      pageSize,
      results,
      _meta: {
        totalCount: filtered.length > 0 ? filtered[0].rows : 0,
        totalPage: totalPage,
        currentPage: page,
        perPage: pageSize
      }
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
