const { errors, APIError } = require('../utils/exceptions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')

const LogBook = require('../models/LogBook')

// eslint-disable-next-line
module.exports = async (req, res) => {
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        // Get request params
        const session = req.user
        let sort = {
            dateTask: -1,
        }
        const page = parseInt(req.query.page) || 1
        const pageSize = parseInt(req.query.pageSize) || 10
        const skip = (page - 1) * pageSize
        const {
            search,
            date,
            sort: _sort,
        } = req.query
        const {
            _id
        } = req.params
        const rules = [{
                $match: {
                    'createdBy._id': _id,
                },
            },
            {
                '$project': {
                    'dateTask': 1,
                    'projectId': 1,
                    'projectName': 1,
                    'nameTask': 1,
                    'difficultyTask': 1,
                    'evidenceTask': 1,
                    'documentTask': 1,
                    'isDocumentLink': 1,
                    'isMainTask': 1,
                    'organizerTask': 1,
                    'otherInformation': 1
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
                '$month': {
                    'dateTask': new Date(date),
                }
            })

        }

        // Get page count
        const count = await LogBook.countDocuments({
            'createdBy.email': session.email
        })
        const filtered = await LogBook.aggregate([
            ...rules,
            {
                '$group': {
                    _id: null,
                    rows: {
                        '$sum': 1
                    }
                },
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
            .skip(skip)
            .limit(pageSize)
            .sort(sort)

        res.status(200).json({
            filtered: filtered.length > 0 ? filtered[0].rows : 0,
            pageSize,
            results,
            _meta: {
                totalCount: count,
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
