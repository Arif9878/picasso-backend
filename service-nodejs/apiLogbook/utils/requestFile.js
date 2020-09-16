const {
    s3
} = require('../utils/aws')
const {
    getRandomString
} = require('../utils/randomString')

async function postFile(fileType, file) {
    let fileName = getRandomString(32)
    if (file.name) {
        fileName = file.name
    }
    const fileExt = fileName.substr((Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1)
    const newFileName = getRandomString(32) + '.' + fileExt
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: file.data,
        Key: `${fileType}/${newFileName}`
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

async function updateFile(lastFilePath, fileType, file) {

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
    if (file.name) {
        fileName = file.name
    }
    const fileExt = fileName.substr((Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1)
    const newFileName = getRandomString(32) + '.' + fileExt
    const params = {
        Bucket: process.env.AWS_S3_BUCKET,
        Body: file.data,
        Key: `${fileType}/${newFileName}`
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
    updateFile
}
