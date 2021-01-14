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

	tracer, _, err := utils.GetJaegerTracer(JaegerHost, "master-jabatan-api")

	if err != nil {
		log.Fatal("cannot initialize Jaeger Tracer", err)
	}

	router.HandleFunc("/api/jabatan/list", config.listJabatan).Methods("GET")
	router.HandleFunc("/api/jabatan/create", config.postJabatan).Methods("POST")
	router.HandleFunc("/api/jabatan/list/by-satuan-kerja/{id}", config.listJabatanBySatuanKerja).Methods("GET")
	router.HandleFunc("/api/jabatan/update/{id}", config.putJabatan).Methods("PUT")
	router.HandleFunc("/api/jabatan/detail/{id}", config.detailJabatan).Methods("GET")
	router.HandleFunc("/api/jabatan/delete/{id}", config.deleteJabatan).Methods("DELETE")

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
	err := utils.SentryTracer(utils.GetEnv("SENTRY_DSN_GOLANG"))
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
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
