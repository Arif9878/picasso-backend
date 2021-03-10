const {
    s3
} = require('../utils/aws')
const {
    getRandomString
} = require('../utils/randomString')
const zlib = require('zlib')
const moment = require('moment')

function postFile(dateTask, fileType, nameFile, buffer) {
    const date = moment(dateTask).format('YYYY-MM-DD')
    
    const fileExt = nameFile.substr((Math.max(0, nameFile.lastIndexOf(".")) || Infinity) + 1)
    const newFileName = getRandomString(40) + '.' + fileExt
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: buffer,
        Key: `${fileType}/${date}/${newFileName}`
    }

    try {
        return new Promise(resolve => {
            s3.upload(params, function (err, data) {
                //handle error
                if (err) {
                    console.error(err)
                }
                //success
                if (data) {
                    const response = {
                        filePath: data.Key,
                        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${data.Key}`
                    }
                    resolve(response)
                }
            })
        })
    } catch (err) {
        reject(err)
    }
}

function updateFile(dateTask, lastFilePath, fileType, nameFile, buffer) {
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
        new Promise(resolve => {
            s3.deleteObjects(deleteParam, function (err, data) {
                if (err) {
                    reject(err)
                } 
                resolve(data)
            })
        })
    }

    const fileExt = nameFile.substr((Math.max(0, nameFile.lastIndexOf(".")) || Infinity) + 1)
    const newFileName = getRandomString(40) + '.' + fileExt
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: buffer,
        Key: `${fileType}/${date}/${newFileName}`
    }

    try {
        return new Promise(resolve => {
            s3.upload(params, function (err, data) {
                //handle error
                if (err) {
                    console.error(err)
                }
                //success
                if (data) {
                    const response = {
                        filePath: data.Key,
                        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${data.Key}`
                    }
                    resolve(response)
                }
            })
        })
    } catch (err) {
        reject(err)
    }
}

function postBlobsFile(dateTask, fileType, blobFile) {
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
    try {
        return new Promise(resolve => {
            s3.upload(params, function (err, data) {
                //handle error
                if (err) {
                    console.error(err)
                }
                //success
                if (data) {
                    const response = {
                        filePath: data.Key,
                        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${data.Key}`
                    }
                    resolve(response)
                }
            })
        })
    } catch (err) {
        reject(err)
    }
}

function updateBlobsFile(dateTask, lastFilePath, fileType, blobFile) {
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
        new Promise(resolve => {
            s3.deleteObjects(deleteParam, function (err, data) {
                if (err) {
                    reject(err)
                } 
                resolve(data)
            })
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
    try {
        return new Promise(resolve => {
            s3.upload(params, function (err, data) {
                //handle error
                if (err) {
                    console.error(err)
                }
                //success
                if (data) {
                    const response = {
                        filePath: data.Key,
                        fileURL: process.env.AWS_S3_CLOUDFRONT + `/${data.Key}`
                    }
                    resolve(response)
                }
            })
        })
    } catch (err) {
        reject(err)
    }
}

module.exports = {
    postFile,
    updateFile,
    postBlobsFile,
    updateBlobsFile
}
