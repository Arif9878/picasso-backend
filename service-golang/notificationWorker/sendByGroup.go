package main

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/appleboy/go-fcm"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func sendByGroup(config *ConfigDB, data []byte) {
	var parseData map[string]interface{}
	json.Unmarshal(data, &parseData)
	message := parseData["message"].(string)
	groupID := parseData["groupID"].(string)
	listUser := getListUserByGroup(groupID)
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	nameDB := utils.GetEnv("MONGO_DB_NOTIFICATION_TOKEN")
	collection := config.db.Collection(nameDB)
	projection := bson.D{
		{"_id", 0},
		{"deviceToken", 1},
	}
	// fmt.Println('',listUser)
	cursor, err := collection.Find(ctx, bson.M{"userID": bson.M{"$in": listUser}}, options.Find().SetProjection(projection))
	if err != nil {
		log.Fatal(err)
	}
	type deviceToken struct {
		DeviceToken string `bson:"deviceToken" json:"deviceToken"`
	}

	result := []deviceToken{}
	if err = cursor.All(ctx, &result); err != nil {
		log.Fatal(err)
	}

	listToken := []string{}
	for key := range result {
		listToken = append(listToken, result[key].DeviceToken)
	}

	msg := &fcm.Message{
		RegistrationIDs: listToken,
		Priority:        "high",
		Notification: &fcm.Notification{
			Title:       utils.GetEnv("TITLE_NOTIFICATION"),
			Body:        message,
			Icon:        "/img/icons/android-chrome-192x192.png",
			Image:       "https://firebasestorage.googleapis.com/v0/b/sapajds.appspot.com/o/FCMImages%2F59417937_385267968984855_3699827078091243520_o.jpg?alt=media&token=6c19bd46-bb5b-4cee-a47f-7cb35c8d24bb",
			Sound:       "3",
			ClickAction: "https://groupware.digitalservice.id/#/",
			Color:       "green",
		},
	}

	// Create a FCM client to send the message.
	client, err := fcm.NewClient(utils.GetEnv("FCM_SERVER_KEY"))
	if err != nil {
		log.Fatalln(err)
	}

	// Send the message and receive the response without retries.
	client.SendWithRetry(msg, 10)
}
