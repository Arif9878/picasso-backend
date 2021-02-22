const {
    s3
} = require('../utils/aws')
const {
    getRandomString
} = require('../utils/randomString')
const zlib = require('zlib')
const moment = require('moment')

async function postFile(dateTask, fileType, nameFile, buffer) {
    const date = moment(dateTask).format('YYYY-MM-DD')

    let fileName = getRandomString(32)
    if (nameFile) {
        fileName = nameFile
    }
    
    const fileExt = fileName.substr((Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1)
    const newFileName = getRandomString(32) + '.' + fileExt
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: buffer,
        Key: `${fileType}/${date}/${newFileName}`
    }
    const response = {
        filePath: params.Key,
        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${params.Key}`
    }
    await s3.upload(params, async function (err, data) {
        //handle error
        if (err) {
            console.error(err)
        }
        //success
        if (data) {
            return data
        }
    })
    return response
}

async function updateFile(dateTask, lastFilePath, fileType, nameFile, buffer) {
    const date = moment(dateTask).format('YYYY-MM-DD')
    
    const deleteParam = {
        Bucket: process.env.AWS_S3_BUCKET,
        Delete: {
            Objects: [{
                Key: lastFilePath
            }]
        }
    }

    if (lastFilePath !== null) {
        await s3.deleteObjects(deleteParam, function (err, data) {
            if (err) {
                console.error(err)
            }
        })
    }

    let fileName = getRandomString(32)
    if (nameFile) {
        fileName = nameFile
    }

    const fileExt = fileName.substr((Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1)
    const newFileName = getRandomString(32) + '.' + fileExt
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: buffer,
        Key: `${fileType}/${date}/${newFileName}`
    }

    const response = {
        filePath: params.Key,
        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${params.Key}`
    }
    await s3.upload(params, async function (err, data) {
        //handle error
        if (err) {
            console.error(err)
        }
        //success
        if (data) {
            return data
        }
    })
    return response
}

async function postBlobsFile(dateTask, fileType, blobFile) {
    const date = moment(dateTask).format('YYYY-MM-DD')
    const compressedStringAsBuffer = zlib.gzipSync(blobFile)

    const newFileName = getRandomString(32) + '.gzip'
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: compressedStringAsBuffer,
        Key: `${fileType}/${date}/${newFileName}`,
        ContentType: 'text/plain', 
        ContentEncoding: 'gzip' // that's important
    }
    const response = {
        filePath: params.Key,
        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${params.Key}`
    }
    await s3.upload(params, async function (err, data) {
        //handle error
        if (err) {
            console.error(err)
        }
        //success
        if (data) {
            return data
        }
    })
    return response

}

async function updateBlobsFile(dateTask, lastFilePath, fileType, blobFile) {
    const date = moment(dateTask).format('YYYY-MM-DD')

    const deleteParam = {
        Bucket: process.env.AWS_S3_BUCKET,
        Delete: {
            Objects: [{
                Key: lastFilePath
            }]
        }
    }

    if (lastFilePath !== null) {
        await s3.deleteObjects(deleteParam, function (err, data) {
            if (err) {
                console.error(err)
            }
        })
    }

    const compressedStringAsBuffer = zlib.gzipSync(blobFile)

    const newFileName = getRandomString(32) + '.gzip'
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: compressedStringAsBuffer,
        Key: `${fileType}/${date}/${newFileName}`,
        ContentType: 'text/plain', 
        ContentEncoding: 'gzip' // that's important
    }
    const response = {
        filePath: params.Key,
        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${params.Key}`
    }
    await s3.upload(params, async function (err, data) {
        //handle error
        if (err) {
            console.error(err)
        }
        //success
        if (data) {
            return data
        }
    })
    return response
}

module.exports = {
    postFile,
    updateFile,
    postBlobsFile,
    updateBlobsFile
}
