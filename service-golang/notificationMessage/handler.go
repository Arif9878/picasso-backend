package main

import (
	"context"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gorilla/mux"

	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func (config *ConfigDB) listNotificationMessage(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_MESSAGE_NOTIFICATION")
	collection := config.db.Collection(nameDB)

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
	cursor, err := collection.Find(ctx, bson.M{}, &findOptions)
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

func (config *ConfigDB) detailNotificationMessage(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_MESSAGE_NOTIFICATION")
	collection := config.db.Collection(nameDB)
	var params = mux.Vars(r)
	id, errID := primitive.ObjectIDFromHex(params["ID"])
	if errID != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "id that you sent is wrong!!!")
		return
	}
	var deviceToken models.DeviceToken
	err := collection.FindOne(ctx, models.DeviceToken{ID: id}).Decode(&deviceToken)
	if err != nil {
		switch err {
		case mongo.ErrNoDocuments:
			utils.ResponseError(w, http.StatusInternalServerError, "device token not found")
		default:
			utils.ResponseError(w, http.StatusInternalServerError, "there is an error on server!!!")
		}
		return
	}
	utils.ResponseOk(w, deviceToken)
}

func (config *ConfigDB) deleteNotificationMessage(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_MESSAGE_NOTIFICATION")
	collection := config.db.Collection(nameDB)
	var params = mux.Vars(r)
	id, err := primitive.ObjectIDFromHex(params["ID"])
	if err != nil {
		utils.ResponseError(w, http.StatusInternalServerError, "id that you sent is wrong!!!")
		return
	}
	result, err := collection.DeleteOne(ctx, models.DeviceToken{ID: id})
	if err != nil {
		log.Printf("Error while updateing document: %v", err)
		utils.ResponseError(w, http.StatusInternalServerError, "error in updating document!!!")
		return
	}
	utils.ResponseOk(w, result)
}
