package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gorilla/mux"
	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func (config *ConfigDB) listHolidayDate(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_HOLIDAY_DATE")
	collection := config.db.Collection(nameDB)
	search := string(r.URL.Query().Get("search"))
	year := string(r.URL.Query().Get("year"))
	page, err := strconv.ParseInt(r.URL.Query().Get("page"), 10, 64)
	if err != nil {
		page = 0
	} else {
		page--
	}

	limit, err := strconv.ParseInt(r.URL.Query().Get("limit"), 10, 64)
	if err != nil {
		limit = 100
	}
	page = page * limit
	findOptions := options.FindOptions{
		Skip:  &page,
		Limit: &limit,
		Sort: bson.M{
			"_id": -1, // -1 for descending and 1 for ascending
		},
	}
	location, err := time.LoadLocation("Asia/Jakarta")
	if err != nil {
		log.Fatal(err)
	}
	var yearTime = time.Now()
	if len(year) > 2 {
		yearInt, err := strconv.Atoi(year)
		if err != nil {
			log.Fatal(err)
		}
		yearTime = time.Date(yearInt, 01, 10, 0, 0, 0, 0, location)
	}
	query := bson.M{
		"holiday_name": primitive.Regex{
			Pattern: search,
			Options: "i",
		},
		"$expr": bson.M{
			"$eq": []interface{}{
				bson.M{"$year": bson.M{"date": "$holiday_date", "timezone": "Asia/Jakarta"}},
				bson.M{"$year": yearTime},
			},
		},
	}
	cursor, err := collection.Find(ctx, query, &findOptions)
	if err != nil {
		log.Fatal(err)
	}
	// var result []bson.M
	var result []models.HolidayDateResponse
	if err = cursor.All(ctx, &result); err != nil {
		log.Fatal(err)
	}
	total, err := collection.CountDocuments(ctx, query)
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

func (config *ConfigDB) postHolidayDate(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 20*time.Second)
	headerCtx := r.Context().Value("user")
	sessionUser := headerCtx.(*jwt.Token).Claims.(jwt.MapClaims)
	delete(sessionUser, "exp")
	delete(sessionUser, "iat")
	sessionUser["_id"] = sessionUser["user_id"]
	delete(sessionUser, "user_id")
	nameDB := utils.GetEnv("MONGO_DB_HOLIDAY_DATE")
	collection := config.db.Collection(nameDB)
	decoder := json.NewDecoder(r.Body)
	payload := models.HolidayDate{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	location, err := time.LoadLocation("Asia/Jakarta")
	if err != nil {
		log.Fatal(err)
	}
	matchStage := bson.M{
		"holiday_date": bson.M{
			"$gte": payload.HolidayDate.In(location),
			"$lt":  payload.HolidayDate.In(location).Add(time.Hour * time.Duration(9)),
		},
	}
	match, err := collection.Find(ctx, matchStage)
	if err != nil {
		log.Fatal(err)
	}
	var resultMatch []bson.M
	if err = match.All(ctx, &resultMatch); err != nil {
		log.Fatal(err)
	}
	if len(resultMatch) != 0 {
		utils.ResponseError(w, http.StatusInternalServerError, "Tanggal tersebut sudah terisi libur")
		return
	}
	create := models.HolidayDate{
		HolidayDate: payload.HolidayDate,
		HolidayType: payload.HolidayType,
		HolidayName: payload.HolidayName,
		CreatedAt:   time.Now(),
		CreatedBy:   sessionUser,
	}
	result, err := collection.InsertOne(ctx, create)
	if err != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "Gagal menyimpan data")
		return
	}
	mod := mongo.IndexModel{
		Keys: bson.M{
			"holiday_name": 1, // index in ascending order
		},
		Options: nil,
	}

	// Create an Index using the CreateOne() method
	_, err = collection.Indexes().CreateOne(ctx, mod)
	if err != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "Gagal menyimpan data")
		return
	}
	utils.ResponseOk(w, result)
}

func (config *ConfigDB) putHolidayDate(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 20*time.Second)
	params := mux.Vars(r)
	headerCtx := r.Context().Value("user")
	sessionUser := headerCtx.(*jwt.Token).Claims.(jwt.MapClaims)
	delete(sessionUser, "exp")
	delete(sessionUser, "iat")
	sessionUser["_id"] = sessionUser["user_id"]
	delete(sessionUser, "user_id")
	nameDB := utils.GetEnv("MONGO_DB_HOLIDAY_DATE")
	collection := config.db.Collection(nameDB)
	id, errID := primitive.ObjectIDFromHex(params["ID"])
	if errID != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "id that you sent is wrong!!!")
		return
	}

	decoder := json.NewDecoder(r.Body)
	payload := models.HolidayDate{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	var holidayDateCheck models.HolidayDate
	err := collection.FindOne(ctx, models.HolidayDate{ID: id}).Decode(&holidayDateCheck)
	if err != nil {
		switch err {
		case mongo.ErrNoDocuments:
			utils.ResponseError(w, http.StatusInternalServerError, "device token not found")
		default:
			utils.ResponseError(w, http.StatusInternalServerError, "there is an error on server!!!")
		}
		return
	} else {
		checkDate := utils.DateEqual(holidayDateCheck.HolidayDate, payload.HolidayDate)
		if checkDate == true {
			holidayData := models.HolidayDate{
				HolidayDate: payload.HolidayDate,
				HolidayType: payload.HolidayType,
				HolidayName: payload.HolidayName,
				UpdatedAt:   time.Now(),
				UpdatedBy:   sessionUser,
			}
			update := bson.M{
				"$set": holidayData,
			}
			result, err := collection.UpdateOne(ctx, models.HolidayDate{ID: id}, update)
			if err != nil {
				utils.ResponseError(w, http.StatusInternalServerError, "Gagal mengubah data")
				return
			}
			utils.ResponseOk(w, result)
		} else {
			location, err := time.LoadLocation("Asia/Jakarta")
			if err != nil {
				log.Fatal(err)
			}
			matchStage := bson.M{
				"holiday_date": bson.M{
					"$gte": payload.HolidayDate.In(location),
					"$lt":  payload.HolidayDate.In(location).Add(time.Hour * time.Duration(9)),
				},
			}
			match, err := collection.Find(ctx, matchStage)
			if err != nil {
				log.Fatal(err)
			}
			var resultMatch []bson.M
			if err = match.All(ctx, &resultMatch); err != nil {
				log.Fatal(err)
			}
			if len(resultMatch) != 0 {
				utils.ResponseError(w, http.StatusInternalServerError, "Tanggal tersebut sudah terisi libur")
				return
			} else {
				holidayData := models.HolidayDate{
					HolidayDate: payload.HolidayDate,
					HolidayType: payload.HolidayType,
					HolidayName: payload.HolidayName,
					UpdatedAt:   time.Now(),
					UpdatedBy:   sessionUser,
				}
				update := bson.M{
					"$set": holidayData,
				}
				result, err := collection.UpdateOne(ctx, models.HolidayDate{ID: id}, update)
				if err != nil {
					utils.ResponseError(w, http.StatusInternalServerError, "Gagal mengubah data")
					return
				}
				utils.ResponseOk(w, result)
			}
		}
	}
}

func (config *ConfigDB) deleteHolidayDate(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	params := mux.Vars(r)
	nameDB := utils.GetEnv("MONGO_DB_HOLIDAY_DATE")
	collection := config.db.Collection(nameDB)
	id, err := primitive.ObjectIDFromHex(params["ID"])
	result, err := collection.DeleteOne(ctx, models.HolidayDate{ID: id})
	if err != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "error in updating document!!!")
		return
	}
	utils.ResponseOk(w, result)
}
