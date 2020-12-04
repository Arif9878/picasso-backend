package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
	auth "github.com/jabardigitalservice/picasso-backend/service-golang/middleware"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
)

func newRouter(config *ConfigDB) (router *mux.Router) {
	router = mux.NewRouter()
	router.HandleFunc("/api/holiday-date/list", config.listHolidayDate).Methods("GET")
	router.HandleFunc("/api/holiday-date/create", config.postHolidayDate).Methods("POST")
	router.HandleFunc("/api/holiday-date/update/{ID}", config.putHolidayDate).Methods("PUT")
	router.HandleFunc("/api/holiday-date/delete/{ID}", config.deleteHolidayDate).Methods("DELETE")
	return
}

func main() {

	configuration, err := Initialize(utils.GetEnv("MONGO_DB_HOLIDAY_DATE"))
	if err != nil {
		log.Println(err)
	}
	// Run HTTP server
	router := newRouter(configuration)
	var port string
	port = ":" + utils.GetEnv("HOLIDAY_DATE_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
