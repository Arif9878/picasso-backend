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
	router.HandleFunc("/api/notification/send/all/", config.sendToAll).Methods("POST")
	router.HandleFunc("/api/notification/send/group/{groupID}", config.sendByGroup).Methods("POST")
	return
}

func main() {

	configuration, err := Initialize()
	if err != nil {
		log.Println(err)
	}
	// Run HTTP server
	router := newRouter(configuration)
	var port string
	port = ":" + utils.GetEnv("NOTIFICATION_SERVICE_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
