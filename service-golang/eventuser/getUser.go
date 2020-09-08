package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"strconv"

	"github.com/bdwilliams/go-jsonify/jsonify"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	_ "github.com/lib/pq"
	"github.com/tidwall/gjson"
)

func getUser(id string) ([]byte, error) {
	postgresHost := utils.GetEnv("POSTGRESQL_HOST")
	postgresPort, errPort := strconv.ParseInt(utils.GetEnv("POSTGRESQL_PORT"), 10, 64)
	postgresUser := utils.GetEnv("POSTGRESQL_USER")
	postgresPassword := utils.GetEnv("POSTGRESQL_PASSWORD")
	postgresDBauth := utils.GetEnv("DB_NAME_AUTH")
	postgresDBmaster := utils.GetEnv("POSTGRESQL_DB_MASTER")
	if errPort != nil {
		fmt.Println(errPort)
	}
	addrAuth := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		postgresHost, postgresPort, postgresUser, postgresPassword, postgresDBauth)
	addrMaster := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		postgresHost, postgresPort, postgresUser, postgresPassword, postgresDBmaster)
	dbAuth, err := sql.Open("postgres", addrAuth)
	dbMaster, err := sql.Open("postgres", addrMaster)
	if err != nil {
		log.Fatal("Failed to open a DB connection: ", err)
	}
	defer dbAuth.Close()
	defer dbMaster.Close()
	userSql := "SELECT accounts_account.id, accounts_account.email, accounts_account.username, accounts_account.first_name, accounts_account.last_name, accounts_account.id_divisi, accounts_account.divisi, accounts_account.id_jabatan, accounts_account.jabatan FROM accounts_account WHERE accounts_account.id = $1"
	jabatanSql := "SELECT description FROM jabatans WHERE id = $1"
	rowsUser, err := dbAuth.Query(userSql, id)
	type notFound struct {
		NotFound string
	}
	if err != nil {
		// log the error
		fmt.Println(err)
		usersBytes, _ := json.Marshal(&notFound{NotFound: "NotFound"})
		return usersBytes, nil
	}

	defer rowsUser.Close()
	defer dbAuth.Close()

	var responseUser = jsonify.Jsonify(rowsUser)
	idJabatan := gjson.Get(responseUser[0], "id_jabatan")
	rowsJabatan, err := dbMaster.Query(jabatanSql, idJabatan.String())

	defer rowsJabatan.Close()
	defer dbMaster.Close()
	var responseJabatan = jsonify.Jsonify(rowsJabatan)
	response := []string{}
	response = append(response, responseUser[0])
	response = append(response, responseJabatan[0])
	usersBytes, _ := json.Marshal(response)
	return usersBytes, nil
}
