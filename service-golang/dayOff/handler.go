package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gorilla/mux"
	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func (config *ConfigDB) listDayOff(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	headerCtx := r.Context().Value("user")
	sessionUser := headerCtx.(*jwt.Token).Claims.(jwt.MapClaims)
	nameDB := utils.GetEnv("MONGO_DB_DAY_OFF")
	collection := config.db.Collection(nameDB)
	idUser := sessionUser["user_id"].(string)
	page, err := strconv.ParseInt(r.URL.Query().Get("page"), 10, 64)
	if err != nil {
		page = 0
	} else {
		page--
	}

	limit, err := strconv.ParseInt(r.URL.Query().Get("limit"), 10, 64)
	if err != nil {
		limit = 20
	}
	page = page * limit
	findOptions := options.FindOptions{
		Skip:  &page,
		Limit: &limit,
		Sort: bson.M{
			"_id": -1, // -1 for descending and 1 for ascending
		},
	}
	cursor, err := collection.Find(ctx, bson.M{"created_by._id": idUser}, &findOptions)
	if err != nil {
		log.Fatal(err)
	}
	var result []bson.M
	if err = cursor.All(ctx, &result); err != nil {
		log.Fatal(err)
	}
	total, err := collection.CountDocuments(ctx, bson.M{})
	if err != nil {
		log.Fatal(err)
	}
	metaData := models.MetaData{
		TotalCount:  int(total),
		TotalPage:   utils.PageCount(int(total), int(limit)),
		CurrentPage: utils.CurrentPage(int(page), int(limit)),
		PerPage:     int(limit),
	}

	results := models.ResultsData{
		Status:  http.StatusOK,
		Success: true,
		Results: result,
		Meta:    metaData,
	}

	utils.ResponseOk(w, results)
}

func (config *ConfigDB) postDayOff(w http.ResponseWriter, r *http.Request) {
	r.ParseMultipartForm(10 << 20)
	AccessKeyID := utils.GetEnv("AWS_S3_ACCESS_KEY")
	SecretAccessKey := utils.GetEnv("AWS_S3_SECRET_ACCESS_KEY")
	MyRegion := utils.GetEnv("AWS_S3_REGION")

	sess := utils.ConnectAws(AccessKeyID, SecretAccessKey, MyRegion)

	MyBucket := utils.GetEnv("AWS_S3_BUCKET")
	ctx, _ := context.WithTimeout(context.Background(), 20*time.Second)
	headerCtx := r.Context().Value("user")
	sessionUser := headerCtx.(*jwt.Token).Claims.(jwt.MapClaims)
	delete(sessionUser, "exp")
	delete(sessionUser, "iat")
	sessionUser["_id"] = sessionUser["user_id"]
	delete(sessionUser, "user_id")
	nameDB := utils.GetEnv("MONGO_DB_DAY_OFF")
	collection := config.db.Collection(nameDB)
	filename := "null"
	resp := "null"
	file, handler, err := r.FormFile("file")
	if err == nil {
		RandomString := utils.String(30)
		exstension := filepath.Ext(handler.Filename)
		filename = RandomString + exstension
		resp, err = utils.UploadFileS3(file, filename, MyBucket, sess)
		if err != nil {
			log.Fatal(err)
		}
		defer file.Close()
	}
	layout := "2006-01-02T15:04:05.000Z"
	ParseStartDate, err := time.Parse(layout, r.PostFormValue("start_date"))
	if err != nil {
		panic(err)
	}
	ParseEndDate, err := time.Parse(layout, r.PostFormValue("end_date"))
	if err != nil {
		panic(err)
	}
	location, err := time.LoadLocation("Asia/Jakarta")
	if err != nil {
		log.Fatal(err)
	}
	listPermit := CheckAttendanceExist(ParseStartDate.In(location), ParseEndDate.In(location))
	if len(listPermit) != 0 {
		utils.ResponseError(w, http.StatusInternalServerError, "Tanggal Sakit/Izin/Cuti Sudah ada")
		return
	}
	for rd := utils.RangeDate(ParseStartDate.In(location), ParseEndDate.In(location)); ; {
		date := rd()
		if date.IsZero() {
			break
		}
		if int(date.Weekday()) != 6 && int(date.Weekday()) != 0 {
			CreateAttendanceDayOff(date, r.PostFormValue("permits_type"), sessionUser)
		}
	}
	split := strings.Split(r.PostFormValue("permit_acknowledged"), ",")
	var arrayPermit []string
	for val := range split {
		arrayPermit = append(arrayPermit, string(split[val]))
	}
	var PermitsTypeUpper = strings.ToUpper(r.PostFormValue("permits_type"))
	create := models.DayOff{
		StartDate:          ParseStartDate,
		EndDate:            ParseEndDate,
		PermitsType:        PermitsTypeUpper
		PermitAcknowledged: arrayPermit,
		Note:               r.PostFormValue("note"),
		FilePath:           filename,
		FileURL:            resp,
		CreatedAt:          time.Now(),
		CreatedBy:          sessionUser,
	}
	result, err := collection.InsertOne(ctx, create)
	if err != nil {
		log.Fatal(err)
	}
	utils.ResponseOk(w, result)
}

func (config *ConfigDB) deleteDayOff(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_DAY_OFF")
	collection := config.db.Collection(nameDB)
	AccessKeyID := utils.GetEnv("AWS_S3_ACCESS_KEY")
	SecretAccessKey := utils.GetEnv("AWS_S3_SECRET_ACCESS_KEY")
	MyRegion := utils.GetEnv("AWS_S3_REGION")
	MyBucket := utils.GetEnv("AWS_S3_BUCKET")
	sess := utils.ConnectAws(AccessKeyID, SecretAccessKey, MyRegion)
	var params = mux.Vars(r)
	id, err := primitive.ObjectIDFromHex(params["ID"])
	if err != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "id that you sent is wrong!!!")
		return
	}
	resp := models.DayOff{}
	err = collection.FindOne(ctx, models.DayOff{ID: id}).Decode(&resp)
	if err != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "Data Not Found")
		return
	}
	if resp.FilePath != "null" {
		_, err = utils.DeleteFileS3(resp.FilePath, MyBucket, sess)
		if err != nil {
			fmt.Println(err)
		}
	}
	location, err := time.LoadLocation("Asia/Jakarta")
	if err != nil {
		log.Fatal(err)
	}
	DeleteAttendanceDayOff(resp.StartDate.In(location), resp.EndDate.In(location), resp.PermitsType)
	result, err := collection.DeleteOne(ctx, models.DayOff{ID: id})
	if err != nil {
		log.Printf("Error while updateing document: %v", err)
		utils.ResponseError(w, http.StatusInternalServerError, "error in updating document!!!")
		return
	}
	utils.ResponseOk(w, result)
}
