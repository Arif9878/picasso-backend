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
	router.HandleFunc("/api/settings/list", config.listSettings).Methods("GET")
	router.HandleFunc("/api/settings/create", config.postSettings).Methods("POST")
	router.HandleFunc("/api/settings/update/{id}", config.putSettings).Methods("PUT")
	router.HandleFunc("/api/settings/delete/{id}", config.deleteSettings).Methods("DELETE")
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
	port = ":" + utils.GetEnv("SETTINGS_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
