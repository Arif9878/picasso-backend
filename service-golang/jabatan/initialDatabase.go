package main

import (
	"fmt"
	"strconv"
	"time"

	db "github.com/jabardigitalservice/picasso-backend/service-golang/db_host"
	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/retry"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/jinzhu/gorm"
)

func Migrate(db *gorm.DB) {
	db.AutoMigrate(&models.Jabatan{})
}

type ConfigDB struct {
	db *gorm.DB
}

func Initialize() (*ConfigDB, error) {

	postgresHost := utils.GetEnv("POSTGRESQL_HOST")
	postgresPort, errPort := strconv.ParseInt(utils.GetEnv("POSTGRESQL_PORT"), 10, 64)
	postgresUser := utils.GetEnv("POSTGRESQL_USER")
	postgresPassword := utils.GetEnv("POSTGRESQL_PASSWORD")
	postgresDB := utils.GetEnv("POSTGRESQL_DB_MASTER")
	if errPort != nil {
		fmt.Println(errPort)
	}
	addr := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		postgresHost, postgresPort, postgresUser, postgresPassword, postgresDB)
	config := ConfigDB{}
	// Connect to PostgreSQL
	retry.ForeverSleep(2*time.Second, func(attempt int) error {
		db := db.Init(addr)
		Migrate(db)

		config.db = db
		return nil
	})
	return &config, nil
}
