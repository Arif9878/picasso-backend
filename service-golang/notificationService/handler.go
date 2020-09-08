package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gorilla/mux"
	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/nats-io/go-nats"
)

func (config *ConfigDB) sendToAll(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	headerCtx := r.Context().Value("user")
	sessionUser := headerCtx.(*jwt.Token).Claims.(jwt.MapClaims)
	delete(sessionUser, "exp")
	delete(sessionUser, "iat")
	nameDB := utils.GetEnv("MONGO_DB_MESSAGE_NOTIFICATION")
	collection := config.db.Collection(nameDB)
	decoder := json.NewDecoder(r.Body)
	payload := models.MessageNotification{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	subject := "broadcastNotification"
	natsUri := utils.GetEnv("NATS_URI")
	opts := nats.Options{
		AllowReconnect: true,
		MaxReconnect:   5,
		ReconnectWait:  5 * time.Second,
		Timeout:        3 * time.Second,
		Url:            natsUri,
	}

	create := models.MessageNotification{
		PurposeMessage: payload.PurposeMessage,
		Message:        payload.Message,
		CreatedBy:      sessionUser,
		CreatedAt:      time.Now(),
	}

	result, err := collection.InsertOne(ctx, create)
	if err != nil {
		log.Fatal(err)
	}
	connNats, _ := opts.Connect()
	connNats.Publish(subject, []byte(payload.Message))
	connNats.Flush()
	utils.ResponseOk(w, result)
}

func (config *ConfigDB) sendByGroup(w http.ResponseWriter, r *http.Request) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	var params = mux.Vars(r)
	headerCtx := r.Context().Value("user")
	sessionUser := headerCtx.(*jwt.Token).Claims.(jwt.MapClaims)
	delete(sessionUser, "exp")
	delete(sessionUser, "iat")
	nameDB := utils.GetEnv("MONGO_DB_MESSAGE_NOTIFICATION")
	collection := config.db.Collection(nameDB)
	decoder := json.NewDecoder(r.Body)
	payload := models.MessageNotification{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	subject := "groupNotification"
	natsUri := utils.GetEnv("NATS_URI")
	opts := nats.Options{
		AllowReconnect: true,
		MaxReconnect:   5,
		ReconnectWait:  5 * time.Second,
		Timeout:        3 * time.Second,
		Url:            natsUri,
	}

	create := models.MessageNotification{
		PurposeMessage: payload.PurposeMessage,
		Message:        payload.Message,
		CreatedBy:      sessionUser,
		CreatedAt:      time.Now(),
	}

	result, err := collection.InsertOne(ctx, create)
	if err != nil {
		log.Fatal(err)
	}
	connNats, _ := opts.Connect()
	data := map[string]interface{}{
		"message": payload.Message,
		"groupID": params["groupID"],
	}
	b, err := json.Marshal(data)
	if err != nil {
		panic(err)
	}
	connNats.Publish(subject, []byte(b))
	connNats.Flush()
	utils.ResponseOk(w, result)
}
