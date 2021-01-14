package main

import (
	"log"
	"runtime"

	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/robfig/cron"
)

func main() {
	log.Println("running job")
	c := cron.New()

	// release purpose:
	c.AddFunc("@daily", func() { checkoutAttendance() })

	// Sentry
	err := utils.SentryTracer(utils.GetEnv("SENTRY_DSN_GOLANG"))
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}

	// debug purpose:
	// checkoutAttendance()

	c.Start()
	runtime.Goexit()
}
