package main

import (
	"time"

	db "github.com/jabardigitalservice/picasso-backend/service-golang/db_host"
	"github.com/jabardigitalservice/picasso-backend/service-golang/retry"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"go.mongodb.org/mongo-driver/mongo"
)

// ConfigDB mongo
type ConfigDB struct {
	mongodb *mongo.Database
}

// Initialize mongodb connection
func Initialize() (*ConfigDB, error) {
	addr := "mongodb://" + utils.GetEnv("DB_MONGO_HOST") + ":" + utils.GetEnv("DB_MONGO_PORT")
	nameDB := utils.GetEnv("MONGO_DB_ATTENDANCE")
	config := ConfigDB{}
	// Connect to MongoDB
	retry.ForeverSleep(2*time.Second, func(attempt int) error {
		mongodb := db.InitMongoDB(addr, nameDB)
		config.mongodb = mongodb
		return nil
	})
	return &config, nil
}
