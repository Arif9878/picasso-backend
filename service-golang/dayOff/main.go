package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync/atomic"
	"time"

	"github.com/gorilla/mux"
	auth "github.com/jabardigitalservice/picasso-backend/service-golang/middleware"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/opentracing-contrib/go-gorilla/gorilla"
)

func newRouter(config *ConfigDB) (router *mux.Router) {
	router = mux.NewRouter()

	JaegerHost := utils.GetEnv("GO_JAEGER_HOST_PORT")

	tracer, _, err := utils.GetJaegerTracer(JaegerHost, "day-off-api")

	if err != nil {
		log.Fatal("cannot initialize Jaeger Tracer", err)
	}
	router.HandleFunc("/api/day-off/list", config.listDayOff).Methods("GET")
	router.HandleFunc("/api/day-off/create", config.postDayOff).Methods("POST")
	router.HandleFunc("/api/day-off/delete/{ID}", config.deleteDayOff).Methods("DELETE")
	router.HandleFunc("/api/day-off/detail/{ID}", config.deleteDayOff).Methods("GET")

	// Add tracing to all routes
	_ = router.Walk(func(route *mux.Route, router *mux.Router, ancestors []*mux.Route) error {
		route.Handler(
			gorilla.Middleware(tracer, route.GetHandler()))
		return nil
	})
	return
}

var (
	listenAddr string
	healthy    int32
	port       string
)

func main() {

	configuration, err := Initialize(utils.GetEnv("MONGO_DB_DAY_OFF"))
	if err != nil {
		log.Println(err)
	}

	// Sentry
	errSentry := utils.SentryTracer(utils.GetEnv("SENTRY_DSN_GOLANG"))
	if errSentry != nil {
		log.Fatalf("sentry.Init: %s", errSentry)
	}

	// Run HTTP server
	router := newRouter(configuration)

	port = ":" + utils.GetEnv("DAY_OFF_PORT")
	if len(port) < 2 {
		port = ":80"
	}

	flag.StringVar(&listenAddr, "listen-addr", port, "server listen address")
	flag.Parse()

	logger := log.New(os.Stdout, "http: ", log.LstdFlags)
	logger.Println("Server is starting...")

	nextRequestID := func() string {
		return fmt.Sprintf("%d", time.Now().UnixNano())
	}

	server := &http.Server{
		Addr:         listenAddr,
		Handler:      auth.Tracing(nextRequestID)(auth.Logging(logger)(auth.AuthMiddleware(router))),
		ErrorLog:     logger,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  15 * time.Second,
	}

	logger.Println("Server is ready to handle requests at", listenAddr)
	atomic.StoreInt32(&healthy, 1)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		logger.Fatalf("Could not listen on %s: %v\n", listenAddr, err)
	}

	// <-done
	logger.Println("Server stopped")
}
