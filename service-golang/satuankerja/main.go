package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"

	auth "github.com/jabardigitalservice/picasso-backend/service-golang/middleware"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/opentracing-contrib/go-gorilla/gorilla"
)

func newRouter(config *ConfigDB) (router *mux.Router) {
	router = mux.NewRouter()

	JaegerHost := utils.GetEnv("GO_JAEGER_HOST_PORT")

	tracer, _, err := utils.GetJaegerTracer(JaegerHost, "master-satuankerja-api")

	if err != nil {
		log.Fatal("cannot initialize Jaeger Tracer", err)
	}

	router.HandleFunc("/api/satuan-kerja/list", config.listSatuanKerja).Methods("GET")
	router.HandleFunc("/api/satuan-kerja/create", config.postSatuanKerja).Methods("POST")
	router.HandleFunc("/api/satuan-kerja/update/{id}", config.putSatuanKerja).Methods("PUT")
	router.HandleFunc("/api/satuan-kerja/detail/{id}", config.detailSatuanKerja).Methods("GET")
	router.HandleFunc("/api/satuan-kerja/delete/{id}", config.deleteSatuanKerja).Methods("DELETE")

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

	// Sentry
	errSentry := utils.SentryTracer(utils.GetEnv("SENTRY_DSN_GOLANG"))
	if err != nil {
		log.Fatalf("sentry.Init: %s", errSentry)
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
