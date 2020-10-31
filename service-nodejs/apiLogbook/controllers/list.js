const { errors, APIError } = require('../utils/exceptions')
const LogBook = require('../models/LogBook')
const moment = require('moment')
moment.locale('id')

// eslint-disable-next-line
module.exports = async (req, res, next) => {
  try {
    // Get request params
    const session = req.user
    let sort = {
      dateTask: 1,
    }
    const page = parseInt(req.query.page) || 1
    const pageSize = parseInt(req.query.pageSize) || 10
    const skip = (page - 1) * pageSize
    const  {
        search,
        start_date,
        end_date,
        sort: _sort
    } = req.query

    const rules = [
      {
        $match: {
          'createdBy.email': session.email
        },
      },
      {
        '$project': {
          'dateTask': 1,
          'projectId': 1,
          'projectName': 1,
          'nameTask': 1,
          'difficultyTask': 1,
          'evidenceTaskURL': '$evidenceTask.fileURL',
          'evidenceTaskPath': '$evidenceTask.filePath',
          'documentTaskURL': { '$ifNull': ['$documentTask.fileURL', ''] },
          'documentTaskPath': { '$ifNull': [ '$documentTask.filePath', '' ] },
          'isDocumentLink': 1,
          'isMainTask': 1,
          'workPlace': 1,
          'organizerTask': 1,
          'otherInformation': { '$ifNull': ['$otherInformation', ''] },
        }
      }
    ]

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
          'nameTask': {
            '$regex': terms,
          },
        },
      })

    }

    if (start_date) {
      let start = moment(start_date).set({
        "hour": 0,
        "minute": 0,
        "second": 0
      }).format()

      let end = moment(end_date).set({
        "hour": 23,
        "minute": 59,
        "second": 59
      }).format()
      
      rules.push({
        '$match': {
          'dateTask': {
            $gte: new Date(start),
            $lt: new Date(end)
          }
        },
      })
    }

    // Get page count
    const filtered = await LogBook.aggregate([
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
    const results = await LogBook
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
  } catch (error) {
    const { code, message, data } = error

    if (code && message) {
        res.status(code).send({
            code,
            message,
            data,
        })
    } else {
        res.status(404).send(errors.notFound)
    }
  }
}
