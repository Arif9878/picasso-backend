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
	router.HandleFunc("/api/satuan-kerja/list", config.listSatuanKerja).Methods("GET")
	router.HandleFunc("/api/satuan-kerja/create", config.postSatuanKerja).Methods("POST")
	router.HandleFunc("/api/satuan-kerja/update/{id}", config.putSatuanKerja).Methods("PUT")
	router.HandleFunc("/api/satuan-kerja/detail/{id}", config.detailSatuanKerja).Methods("GET")
	router.HandleFunc("/api/satuan-kerja/delete/{id}", config.deleteSatuanKerja).Methods("DELETE")
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
	port = ":" + utils.GetEnv("SATUANKERJA_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
