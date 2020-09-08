package main

import (
	"database/sql"
	"fmt"
	"log"
	"strconv"

	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	_ "github.com/lib/pq"
)

func CheckError(err error) {
	if err != nil {
		panic(err)
	}
}

func getListUserByGroup(groupID string) (list []string) {

	// Create DB pool
	postgresHost := utils.GetEnv("POSTGRESQL_HOST")
	postgresPort, errPort := strconv.ParseInt(utils.GetEnv("POSTGRESQL_PORT"), 10, 64)
	postgresUser := utils.GetEnv("POSTGRESQL_USER")
	postgresPassword := utils.GetEnv("POSTGRESQL_PASSWORD")
	postgresDB := utils.GetEnv("DB_NAME_AUTH")
	if errPort != nil {
		fmt.Println(errPort)
	}
	addr := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		postgresHost, postgresPort, postgresUser, postgresPassword, postgresDB)
	db, err := sql.Open("postgres", addr)
	if err != nil {
		log.Fatal("Failed to open a DB connection: ", err)
	}
	defer db.Close()

	// Create an empty user and make the sql query (using $1 for the parameter)

	rows, err := db.Query("SELECT accounts_account.id FROM accounts_account WHERE accounts_account.id_divisi = $1", groupID)
	if err != nil {
		log.Fatal("Failed to open a DB connection: ", err)
	}
	defer rows.Close()
	listUser := []string{}
	for rows.Next() {
		var id string
		err = rows.Scan(&id)
		CheckError(err)
		listUser = append(listUser, id)
	}

	return listUser

}
