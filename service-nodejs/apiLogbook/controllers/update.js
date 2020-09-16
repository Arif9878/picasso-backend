const { errors, APIError } = require('../utils/exceptions')
const {
    onUpdated,
    filePath
} = require('../utils/session')
const {
    validationResult
} = require('express-validator')
const {
    postFile,
    updateFile
} = require('../utils/requestFile')
const {
    encode,
    imageResize,
} = require('../utils/functions')

// Import Model
const LogBook = require('../models/LogBook')
const BlobsFile = require('../models/BlobsFile')

module.exports = async (req, res) => { // eslint-disable-line
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
            _id
        } = req.params
        const resultLogBook = await LogBook.findById({
            _id: _id
        }).lean()
        let evidenceResponse = resultLogBook.evidenceTask
        let documentResponse = resultLogBook.documentTask

        const {
            dateTask = null,
            projectId = null,
            projectName = null,
            nameTask = null,
            difficultyTask = null,
            organizerTask = null,
            isMainTask = null,
            workPlace = null,
            otherInformation = null,
            isDocumentLink = false
        } = req.body
        const isTask = String(isMainTask) === 'true'
        const isLink = String(isDocumentLink) === 'true'
        let dataBlobEvidence = null
        try {
            if (req.files.evidenceTask) {
                evidenceResponse = await updateFile(
                    resultLogBook.evidenceTask.filePath,
                    'image',
                    req.files.evidenceTask
                )
                const miniBuffer = await imageResize(req.files.evidenceTask.data)
                const bytes = new Uint8Array(miniBuffer)
                dataBlobEvidence = 'data:image/png;base64,' + encode(bytes)
            }
        } catch(err) {
            //
        }

        if (isLink) {
            if (req.body.documentTask.length < 0) throw new APIError(errors.serverError)
            let pathURL = req.body.documentTask
            if (req.body.documentTask === 'null') {
                pathURL = null
            }
            documentResponse = {
                filePath: null,
                fileURL: req.body.documentTask
            }
        } else {
            try {
                if (req.files.documentTask) {
                    if (resultLogBook.documentTask.filePath === null) {
                        documentResponse = await postFile('document', req.files.documentTask)
                    } else {
                        documentResponse = await updateFile(
                            resultLogBook.documentTask.filePath,
                            'document',
                            req.files.documentTask
                        )
                    }
                }
            } catch(err) {
                //
            }
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
            workPlace,
            organizerTask,
            otherInformation,
            ...onUpdated(session)
        }

        const results = await LogBook.findByIdAndUpdate(_id, data)
        if (dataBlobEvidence !== null) await BlobsFile.updateOne({
            logBookId: results._id,
        }, {
            blob: dataBlobEvidence
        })
        await res.status(201).send({
            message: 'Update data successfull',
            data: results,
        })

    } catch (error) {
      console.log(error)
      const { code, message, data } = error

      if (code && message) {
          res.status(code).send({
              code,
              message,
              data,
          })
      } else {
          res.status(500).send(errors.serverError)
      }
    }
}
