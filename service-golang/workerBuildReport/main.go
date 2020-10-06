package main

import (
	"fmt"
	"runtime"
	"time"

	"gopkg.in/robfig/cron.v2"
)

func main() {
	c := cron.New()

	now := time.Now()

	c.AddFunc("TZ=Asia/Jakarta 01 33 19 25 * *", func() {
		fmt.Println("Today:", now)

		after := now.AddDate(0, -3, 0)
		fmt.Println("Subtract 1 Month:", after)
	})

	fmt.Printf("Now: %v\n", now)
	c.Start()
	runtime.Goexit()
}
