const { errors, APIError } = require('../utils/exceptions')
const { validationResult } = require('express-validator')
const { onCreated, filePath } = require('../utils/session')
const { postFile, postBlobsFile } = require('../utils/requestFile')
const { encode, imageResize } = require('../utils/functions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')

// Import Model
const LogBook = require('../models/LogBook')

module.exports = async (req, res) => { // eslint-disable-line
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, {
        childOf: parentSpan,
    })
    try {
        const session = req.user
        const errorsValidate = validationResult(req)
        if (!errorsValidate.isEmpty()) {
            res.status(422).json({
                code: 422,
                errors: errorsValidate.array(),
            })
            return
        }

        const {
            dateTask = null,
            projectId = null,
            projectName= null,
            nameTask = null,
            difficultyTask = null,
            organizerTask = null,
            isMainTask = null,
            workPlace = null,
            otherInformation = null,
            isDocumentLink = null
        } = req.body

        if (!req.files || Object.keys(req.files).length === 0) throw new APIError(errors.validationError)
        const miniBuffer = await imageResize(req.files.evidenceTask.data)
        const bytes = new Uint8Array(miniBuffer)
        const dataBlobEvidence = 'data:image/png;base64,' + encode(bytes)
        const blobResponse = await postBlobsFile('gzip', dataBlobEvidence)
        const evidenceResponse = await postFile('image', req.files.evidenceTask.name, miniBuffer)
        let documentResponse = {}
        const isTask = String(isMainTask) === 'true'
        const isLink = String(isDocumentLink) === 'true'
        if (isLink) {
            if (req.body.documentTask.length < 0) throw new APIError(errors.validationError)
            let pathURL = req.body.documentTask
            if (req.body.documentTask === 'null') {
                pathURL = null
            }
            documentResponse = {
                filePath: '',
                fileURL: pathURL
            }
        } else {
            const miniBuffer = await imageResize(req.files.documentTask.data)
            documentResponse = await postFile('document', req.files.documentTask.name, miniBuffer)
        }

        const data = {
          dateTask,
          projectId,
          projectName,
          nameTask,
          isDocumentLink: isLink,
          isMainTask: isTask,
          difficultyTask,
          evidenceTask: filePath(evidenceResponse),
          documentTask: filePath(documentResponse),
          blobTask: filePath(blobResponse),
          workPlace,
          organizerTask,
          otherInformation,
          ...onCreated(session)
        }

        const results = await LogBook.create(data)

        await res.status(201).send({
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
