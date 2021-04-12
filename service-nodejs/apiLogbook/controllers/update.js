const { errors, APIError } = require('../utils/exceptions')
const { onUpdated, filePath } = require('../utils/session')
const { validationResult } = require('express-validator')
const { postFile, updateFile, updateBlobsFile } = require('../utils/requestFile')
const { encode, imageResize, getTupoksiJabatanDetail, stringIsAValidUrl } = require('../utils/functions')
const { tracer } = require('../utils/tracer')
const opentracing = require('opentracing')

// Import Model
const LogBook = require('../models/LogBook')

module.exports = async (req, res) => { // eslint-disable-line
    const parentSpan = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan(req.originalUrl, { childOf: parentSpan })
    try {
        const session = req.user
        const errorsValidate = validationResult(req)
        if (!errorsValidate.isEmpty()) return res.status(422).json({ code: 422, errors: errorsValidate.array() })

        const {
            _id
        } = req.params
        const resultLogBook = await LogBook.findById({
            _id: _id
        }).lean()

        let evidenceResponse = resultLogBook.evidenceTask
        let blobResponse = resultLogBook.blobTask

        const {
            dateTask = null,
            tupoksiJabatanId = null,
            projectId = null,
            projectName = null,
            nameTask = null,
            difficultyTask = null,
            organizerTask = null,
            documentTask = null,
            workPlace = null,
            otherInformation = null
        } = req.body

        // check tupoksi jabatan and document link url
        if (tupoksiJabatanId !== process.env.TUPOKSI_DILUAR_TUGAS && !documentTask) throw new APIError(errors.documentNotFound)

        // check valid url
        if (documentTask && !stringIsAValidUrl(documentTask)) throw new APIError(errors.urlLinkInvalid)

        // get tupoksi jabatan
        let tupoksiJabatanName = null
        if (tupoksiJabatanId) {
            const detail = await getTupoksiJabatanDetail(tupoksiJabatanId)
            if (detail) {
                tupoksiJabatanName = detail.Value.name_tupoksi
            } else {
                return res.status(500).send(errors.tupoksiNotFound)
            }
        }

        // update image evidence
        let dataBlobEvidence = null
        try {
            if (req.files.evidenceTask) {
                const miniBuffer = await imageResize(req.files.evidenceTask.data)
                const bytes = new Uint8Array(miniBuffer)
                dataBlobEvidence = 'data:image/png;base64,' + encode(bytes)
                const resp = await Promise.all([
                    updateFile(dateTask, resultLogBook.evidenceTask.filePath, 'image', req.files.evidenceTask.name, miniBuffer),
                    updateBlobsFile(dateTask, resultLogBook.blobTask.filePath, 'gzip', dataBlobEvidence)
                ])
                evidenceResponse = resp[0]
                blobResponse = resp[1]
            }
            if (!evidenceResponse.filePath) throw new APIError(errors.evidenceError)
        } catch(err) {
            //
        }

        // update document link
        console.log(documentTask)
        const documentResponse = { filePath: '', fileURL: documentTask }

        const data = {
            dateTask,
            tupoksiJabatanId,
            tupoksiJabatanName: tupoksiJabatanName,
            projectId,
            projectName,
            nameTask,
            difficultyTask,
            evidenceTask: filePath(evidenceResponse),
            documentTask: filePath(documentResponse),
            blobTask: filePath(blobResponse),
            workPlace,
            organizerTask,
            otherInformation,
            ...onUpdated(session)
        }

        const results = await LogBook.findByIdAndUpdate(_id, data)

        await res.status(201).send({
            message: 'Update data successfull',
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
