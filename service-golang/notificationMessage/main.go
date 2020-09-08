package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
)

func newRouter(config *ConfigDB) (router *mux.Router) {
	router = mux.NewRouter()
	router.HandleFunc("/api/notification-message/list", config.listNotificationMessage).Methods("GET")
	router.HandleFunc("/api/notification-message/detail/{ID}", config.detailNotificationMessage).Methods("GET")
	router.HandleFunc("/api/notification-message/delete/{ID}", config.deleteNotificationMessage).Methods("DELETE")
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
	port = ":" + utils.GetEnv("NOTIFICATION_MESSAGE_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, router); err != nil {
		log.Fatal(err)
	}
}
