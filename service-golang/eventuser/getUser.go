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

	userSql := "SELECT accounts_account.id, accounts_account.email, accounts_account.username, accounts_account.first_name, accounts_account.last_name, accounts_account.id_divisi, accounts_account.divisi, accounts_account.id_jabatan, accounts_account.jabatan, accounts_account.manager_category FROM accounts_account WHERE accounts_account.id = $1"
	jabatanSql := "SELECT name_tupoksi FROM tupoksi_jabatans INNER JOIN jabatans ON jabatan_id=jabatans.id WHERE jabatan_id = $1 AND tupoksi_jabatans.deleted_at IS NULL;"

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
	var TupoksiJabatans []string
	if rowsJabatan != nil {
		for rowsJabatan.Next() {
			var name_tupoksi string
			err := rowsJabatan.Scan(&name_tupoksi)
			if err != nil {
				log.Fatal(err)
			}

			TupoksiJabatans = append(TupoksiJabatans, name_tupoksi)
		}
	}
	data := map[string]interface{}{
		"user":    responseUser[0],
		"tupoksi": TupoksiJabatans,
	}

	usersBytes, _ := json.Marshal(data)
	return usersBytes, nil
}
