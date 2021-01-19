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

	tracer, _, err := utils.GetJaegerTracer(JaegerHost, "master-tupoksi-jabatan-api")

	if err != nil {
		log.Fatal("cannot initialize Jaeger Tracer", err)
	}

	router.HandleFunc("/api/tupoksi-jabatan/list", config.listTupoksiJabatan).Methods("GET")
	router.HandleFunc("/api/tupoksi-jabatan/by-user", config.listTupoksiJabatanByUser).Methods("GET")
	router.HandleFunc("/api/tupoksi-jabatan/create", config.postTupoksiJabatan).Methods("POST")
	router.HandleFunc("/api/tupoksi-jabatan/update/{id}", config.putTupoksiJabatan).Methods("PUT")
	router.HandleFunc("/api/tupoksi-jabatan/detail/{id}", config.detailTupoksiJabatan).Methods("GET")
	router.HandleFunc("/api/tupoksi-jabatan/delete/{id}", config.deleteTupoksiJabatan).Methods("DELETE")

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
	port = ":" + utils.GetEnv("TUPOKSI_JABATAN_PORT")
	if len(port) < 2 {
		port = ":80"
	}
	if err := http.ListenAndServe(port, auth.AuthMiddleware(router)); err != nil {
		log.Fatal(err)
	}
}
