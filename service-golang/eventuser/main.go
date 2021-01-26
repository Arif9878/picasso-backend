package main

import (
	"fmt"
	"log"
	"runtime"
	"time"

	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
	"github.com/nats-io/go-nats"
)

func main() {
	subject := "userDetail"
	natsUri := utils.GetEnv("NATS_URI")
	opts := nats.Options{
		AllowReconnect: true,
		MaxReconnect:   5,
		ReconnectWait:  5 * time.Second,
		Timeout:        3 * time.Second,
		Url:            natsUri,
	}
	conn, _ := opts.Connect()
	//defer conn.Close()
	fmt.Println("Subscriber connected to NATS server")

	fmt.Printf("Subscribing to subject %s\n", subject)
	conn.Subscribe(subject, func(msg *nats.Msg) {
		msgResp, err := getUser(string(msg.Data))
		if err != nil {
			fmt.Println(err)
		}
		conn.Publish(msg.Reply, msgResp)
	})

	// Sentry
	err := utils.SentryTracer(utils.GetEnv("SENTRY_DSN_GOLANG"))
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}

	runtime.Goexit()
}
