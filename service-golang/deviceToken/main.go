package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/opentracing-contrib/go-gorilla/gorilla"
)

func newRouter(config *ConfigDB) (router *mux.Router) {
	router = mux.NewRouter()

	JaegerHost := utils.GetEnv("GO_JAEGER_HOST_PORT")

	tracer, _, err := utils.GetJaegerTracer(JaegerHost, "device-token-api")

	if err != nil {
		log.Fatal("cannot initialize Jaeger Tracer", err)
	}

	router.HandleFunc("/api/device-token/list", config.listDeviceToken).Methods("GET")
	router.HandleFunc("/api/device-token/create", config.postDeviceToken).Methods("POST")
	router.HandleFunc("/api/device-token/update/{userID}", config.putDeviceToken).Methods("PUT")
	router.HandleFunc("/api/device-token/detail/{userID}", config.detailDeviceToken).Methods("GET")
	router.HandleFunc("/api/device-token/delete/{userID}", config.deleteDeviceToken).Methods("DELETE")

	// Add tracing to all routes
	_ = router.Walk(func(route *mux.Route, router *mux.Router, ancestors []*mux.Route) error {
		route.Handler(
			gorilla.Middleware(tracer, route.GetHandler()))
		return nil
	})
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
	port = ":" + utils.GetEnv("DEVICE_TOKEN_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, router); err != nil {
		log.Fatal(err)
	}
}
