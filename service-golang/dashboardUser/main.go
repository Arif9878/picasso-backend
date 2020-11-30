package main

import (
	"fmt"
	"log"
	"time"
)

func main() {
	location, err := time.LoadLocation("Asia/Jakarta")
	if err != nil {
		log.Fatal(err)
	}
	t := time.Date(2020, 12, 01, 0, 0, 0, 0, location)
	fmt.Printf("%s\n", t)
	f := time.Date(2020, 12, 31, 24, 0, 0, 0, location)
	fmt.Printf("%s\n", f)
	days := 0
	for {
		if t.Equal(f) {
			break
		}
		if t.Weekday() != time.Saturday && t.Weekday() != time.Sunday {
			days++
		}
		t = t.Add(time.Hour * 24)
	}

	fmt.Printf("Bussnise days %d\n", days)
}
