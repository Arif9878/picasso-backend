package utils

import (
	"fmt"
	"io"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

func ConnectAws(AccessKeyID string, SecretAccessKey string, MyRegion string) *session.Session {
	sess, err := session.NewSession(
		&aws.Config{
			Region: aws.String(MyRegion),
			Credentials: credentials.NewStaticCredentials(
				AccessKeyID,
				SecretAccessKey,
				"", // a token will be created when the session it's used.
			),
		})

	if err != nil {
		panic(err)
	}

	return sess
}

func UploadFileS3(file io.Reader, filename string, bucket string, sess *session.Session) (string, error) {
	uploader := s3manager.NewUploader(sess)
	//upload to the s3 bucket
	_, err := uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(filename),
		Body:   file,
	})

	if err != nil {
		fmt.Println(err)
	}
	fileurl := GetEnv("AWS_S3_CLOUDFRONT") + string('/') + filename
	return fileurl, nil
}

func DeleteFileS3(filename string, bucket string, sess *session.Session) (*s3.DeleteObjectsOutput, error) {
	svc := s3.New(sess)
	input := &s3.DeleteObjectsInput{
		Bucket: aws.String(bucket),
		Delete: &s3.Delete{
			Objects: []*s3.ObjectIdentifier{
				{
					Key: aws.String(filename),
				},
			},
			Quiet: aws.Bool(false),
		},
	}

	resp, err := svc.DeleteObjects(input)
	if err != nil {
		if aerr, ok := err.(awserr.Error); ok {
			switch aerr.Code() {
			default:
				fmt.Println(aerr.Error())
			}
		} else {
			// Print the error, cast err to awserr.Error to get the Code and
			fmt.Println(err.Error())
		}
	}

	return resp, nil
}

func PutFileS3(file io.Reader, filename string, bucket string, sess *session.Session) (*s3.PutObjectOutput, error) {
	svc := s3.New(sess)
	input := &s3.PutObjectInput{
		Body:   aws.ReadSeekCloser(file),
		Bucket: aws.String(bucket),
		Key:    aws.String(filename),
	}

	result, err := svc.PutObject(input)
	if err != nil {
		if aerr, ok := err.(awserr.Error); ok {
			switch aerr.Code() {
			default:
				fmt.Println(aerr.Error())
			}
		} else {
			// Print the error, cast err to awserr.Error to get the Code and
			// Message from an error.
			fmt.Println(err.Error())
		}
	}

	fmt.Println(result)
	return result, nil
}
