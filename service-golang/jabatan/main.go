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
	router.HandleFunc("/api/jabatan/list", config.listJabatan).Methods("GET")
	router.HandleFunc("/api/jabatan/create", config.postJabatan).Methods("POST")
	router.HandleFunc("/api/jabatan/list/by-satuan-kerja/{id}", config.listJabatanBySatuanKerja).Methods("GET")
	router.HandleFunc("/api/jabatan/update/{id}", config.putJabatan).Methods("PUT")
	router.HandleFunc("/api/jabatan/detail/{id}", config.detailJabatan).Methods("GET")
	router.HandleFunc("/api/jabatan/delete/{id}", config.deleteJabatan).Methods("DELETE")
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
	port = ":" + utils.GetEnv("JABATAN_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
