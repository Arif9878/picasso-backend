package db

import (
	"context"
	"log"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var MongoDB *mongo.Database

func InitMongoDB(url string, nameDB string) *mongo.Database {
	client, err := mongo.Connect(
		context.Background(),
		options.Client().ApplyURI(url),
	)

	if err != nil {
		log.Fatal(err)
	}
	MongoDB = client.Database(nameDB)
	return MongoDB
}

// Using this function to get a connection, you can create your connection pool here.
func GetMongoDB() *mongo.Database {
	return MongoDB
}
