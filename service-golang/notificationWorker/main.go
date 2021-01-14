package main

import (
	"fmt"
	"log"
	"runtime"
	"sync"
	"time"

	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/nats-io/go-nats"
	"github.com/robfig/cron"
)

func main() {
	log.Println("running job")
	config, err := Initialize()

	if err != nil {
		log.Println(err)
	}

	subjectSendToAll := "broadcastNotification"
	subjectSendByGroup := "groupNotification"
	natsUri := utils.GetEnv("NATS_URI")
	opts := nats.Options{
		AllowReconnect: true,
		MaxReconnect:   5,
		ReconnectWait:  5 * time.Second,
		Timeout:        3 * time.Second,
		Url:            natsUri,
	}
	conn, _ := opts.Connect()
	fmt.Println("Subscriber connected to NATS server")
	fmt.Printf("Subscribing to subject %s\n", subjectSendToAll)
	fmt.Printf("Subscribing to subject %s\n", subjectSendByGroup)
	conn.Subscribe(subjectSendToAll, func(msg *nats.Msg) {
		sendToAll(config, string(msg.Data))
	})

	conn.Subscribe(subjectSendByGroup, func(msg *nats.Msg) {
		sendByGroup(config, msg.Data)
	})

	wg := &sync.WaitGroup{}
	wg.Add(1)
	c := cron.New()
	c.AddFunc(utils.GetEnv("CHECKIN_CRON_JOB_CHECKIN"), func() { cronJobSendToAllCheckin(config) })
	c.AddFunc(utils.GetEnv("CHECKIN_CRON_JOB_CHECKOUT"), func() { cronJobSendToAllCheckout(config) })
	c.Start()
	wg.Wait()

	// Sentry
	err := utils.SentryTracer(utils.GetEnv("SENTRY_DSN_GOLANG"))
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}

	runtime.Goexit()
}
