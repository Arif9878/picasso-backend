package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/mux"

	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

func (config *ConfigDB) listDeviceToken(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_NOTIFICATION_TOKEN")
	collection := config.db.Collection(nameDB)
	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil {
		log.Fatal(err)
	}
	var result []bson.M
	if err = cursor.All(ctx, &result); err != nil {
		log.Fatal(err)
	}
	utils.ResponseOk(w, result)
}

func (config *ConfigDB) postDeviceToken(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_NOTIFICATION_TOKEN")
	collection := config.db.Collection(nameDB)
	payload := new(models.DeviceToken)
	err := json.NewDecoder(r.Body).Decode(payload)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	count, _ := collection.CountDocuments(ctx, models.DeviceToken{UserID: payload.UserID})
	if count == 1 {
		utils.ResponseError(w, http.StatusBadRequest, "userID is exist")
		return
	} else {
		result, err := collection.InsertOne(ctx, payload)
		if err != nil {
			log.Fatal(err)
		}
		utils.ResponseOk(w, result)
	}
}

func (config *ConfigDB) putDeviceToken(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_NOTIFICATION_TOKEN")
	collection := config.db.Collection(nameDB)
	var updateData map[string]interface{}
	err := json.NewDecoder(r.Body).Decode(&updateData)
	if err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "json body is incorrect")
		return
	}
	// we dont handle the json decode return error because all our fields have the omitempty tag.
	var params = mux.Vars(r)
	if err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "id that you sent is wrong!!!")
		return
	}
	update := bson.M{
		"$set": updateData,
	}
	result, err := collection.UpdateOne(ctx, models.DeviceToken{UserID: params["userID"]}, update)
	if err != nil {
		log.Printf("Error while updateing document: %v", err)
		utils.ResponseError(w, http.StatusInternalServerError, "error in updating document!!!")
		return
	}
	if result.MatchedCount == 1 {
		utils.ResponseOk(w, result)
	} else {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
	}
}

func (config *ConfigDB) detailDeviceToken(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_NOTIFICATION_TOKEN")
	collection := config.db.Collection(nameDB)
	var params = mux.Vars(r)
	var deviceToken models.DeviceToken
	err := collection.FindOne(ctx, models.DeviceToken{UserID: params["userID"]}).Decode(&deviceToken)
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

func (config *ConfigDB) deleteDeviceToken(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_NOTIFICATION_TOKEN")
	collection := config.db.Collection(nameDB)
	var params = mux.Vars(r)
	result, err := collection.DeleteOne(ctx, models.DeviceToken{UserID: params["userID"]})
	if err != nil {
		log.Printf("Error while updateing document: %v", err)
		utils.ResponseError(w, http.StatusInternalServerError, "error in updating document!!!")
		return
	}
	utils.ResponseOk(w, result)
}
