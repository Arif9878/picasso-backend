package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

func checkoutAttendance() {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	configuration, err := Initialize()

	if err != nil {
		log.Println(err)
	}

	collection := configuration.mongodb.Collection("attendances")
	matchStage := bson.D{{"$match", bson.D{{"officeHours", 0}}}}

	result, err := collection.Aggregate(ctx, mongo.Pipeline{matchStage})
	if err != nil {
		panic(err)
	}
	var data []bson.M
	if err = result.All(ctx, &data); err != nil {
		panic(err)
	}

	for i := 0; i < len(data); i++ {
		id := data[i]["_id"]

		startDate := data[i]["startDate"]
		strDate := fmt.Sprintf("%v", startDate)
		strDateSlice := strDate[0:10]
		i, err := strconv.ParseInt(strDateSlice, 10, 64)
		if err != nil {
			panic(err)
		}
		tm := time.Unix(i, 0)
		endDate := time.Unix(tm.Unix(), 0).Add(time.Hour*time.Duration(9) +
			time.Minute*time.Duration(0) +
			time.Second*time.Duration(0))

		// db update attendaces
		filter := bson.D{{"_id", id}}
		update := bson.D{{"$set",
			bson.D{
				{"officeHours", 9},
				{"endDate", endDate},
			},
		}}

		collection.UpdateOne(
			ctx,
			filter,
			update,
		)
	}
}
