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
	router.HandleFunc("/api/day-off/list", config.listDayOff).Methods("GET")
	router.HandleFunc("/api/day-off/create", config.postDayOff).Methods("POST")
	router.HandleFunc("/api/day-off/delete/{ID}", config.deleteDayOff).Methods("DELETE")
	router.HandleFunc("/api/day-off/detail/{ID}", config.deleteDayOff).Methods("GET")
	return
}

func main() {

	configuration, err := Initialize(utils.GetEnv("MONGO_DB_DAY_OFF"))
	if err != nil {
		log.Println(err)
	}
	// Run HTTP server
	router := newRouter(configuration)
	var port string
	port = ":" + utils.GetEnv("DAY_OFF_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
