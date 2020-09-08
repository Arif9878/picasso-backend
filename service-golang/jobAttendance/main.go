package main

import (
	"log"
	"runtime"

	"github.com/robfig/cron"
)

func main() {
	log.Println("running job")
	c := cron.New()

	// release purpose:
	c.AddFunc("@daily", func() { checkoutAttendance() })

	// debug purpose:
	// checkoutAttendance()

	c.Start()
	runtime.Goexit()
}
