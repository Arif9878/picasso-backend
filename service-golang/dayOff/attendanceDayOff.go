package main

import (
	"context"
	"log"
	"time"

	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

func CreateAttendanceDayOff(Date time.Time, PermitsType string, Session map[string]interface{}) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	configuration, err := Initialize(utils.GetEnv("MONGO_DB_ATTENDANCE"))

	if err != nil {
		log.Println(err)
	}
	collection := configuration.db.Collection("attendances")
	EndDate := time.Unix(Date.Unix(), 0).Add(time.Hour * time.Duration(23))
	matchStage := bson.M{"start_date": bson.M{"$gte": Date, "$lt": EndDate}}
	cursor, err := collection.Find(ctx, matchStage)
	if err != nil {
		log.Fatal(err)
	}
	var result []bson.M
	if err = cursor.All(ctx, &result); err != nil {
		log.Fatal(err)
	}
	if len(result) == 0 {
		create := models.Attendance{
			StartDate:   Date,
			EndDate:     Date,
			OfficeHours: int32(0),
			Location:    "-",
			Message:     PermitsType,
			CreatedAt:   time.Now(),
			UpdatedAt:   nil,
			CreatedBy:   Session,
		}
		_, err = collection.InsertOne(ctx, create)
	}
}

func DeleteAttendanceDayOff(StartDate time.Time, EndDate time.Time, PermitsType string) {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	configuration, err := Initialize(utils.GetEnv("MONGO_DB_ATTENDANCE"))

	if err != nil {
		log.Println(err)
	}
	y, m, d := StartDate.Date()
	start := time.Date(y, m, d, 0, 0, 0, 0, time.UTC)
	y, m, d = EndDate.Date()
	end := time.Date(y, m, d, 1, 0, 0, 0, time.UTC)
	collection := configuration.db.Collection("attendances")
	matchStage := bson.M{"message": PermitsType, "startDate": bson.M{"$gte": start, "$lt": end}}
	cursor, err := collection.Find(ctx, matchStage)
	if err != nil {
		log.Fatal(err)
	}
	var result []bson.M
	if err = cursor.All(ctx, &result); err != nil {
		log.Fatal(err)
	}
	if len(result) != 0 {
		for val := range result {
			ObjectID := result[val]["_id"].(primitive.ObjectID)
			_, err := collection.DeleteOne(ctx, models.Attendance{ID: ObjectID})
			if err != nil {
				log.Fatal(err)
			}
		}
	}
}

func CheckAttendanceExist(StartDate time.Time, EndDate time.Time) []bson.M {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	configuration, err := Initialize(utils.GetEnv("MONGO_DB_ATTENDANCE"))
	if err != nil {
		log.Println(err)
	}
	y, m, d := StartDate.Date()
	start := time.Date(y, m, d, 0, 0, 0, 0, time.UTC)
	y, m, d = EndDate.Date()
	end := time.Date(y, m, d, 1, 0, 0, 0, time.UTC)
	collection := configuration.db.Collection("attendances")
	matchStage := bson.M{"startDate": bson.M{"$gte": start, "$lt": end}}
	cursor, err := collection.Find(ctx, matchStage)
	if err != nil {
		log.Fatal(err)
	}
	var listPermit []bson.M
	if err = cursor.All(ctx, &listPermit); err != nil {
		log.Fatal(err)
	}
	return listPermit
}
