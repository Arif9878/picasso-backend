const AWS = require('aws-sdk')

//configuring the AWS environment
AWS.config.update({
    accessKeyId: process.env.AWS_S3_ACCESS_KEY,
    secretAccessKey: process.env.AWS_S3_SECRET_ACCESS_KEY
});

const s3 = new AWS.S3();

module.exports = {
    s3
}
