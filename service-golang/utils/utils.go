package utils

import (
	"encoding/json"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/joho/godotenv"
)

const (
	// DefaultLimit defines the default number of items per page for API responses
	DefaultLimit int = 25

	// DefaultOffset defines the default offset for API responses
	DefaultOffset int = 0
)

func ResponseOk(w http.ResponseWriter, body interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	json.NewEncoder(w).Encode(body)
}

func ResponseError(w http.ResponseWriter, code int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)

	results := models.ErrorResults{
		Code:    code,
		Message: message,
	}

	json.NewEncoder(w).Encode(results)
}

func PageCount(total int, limit int) int {
	if limit == 0 {
		limit = DefaultLimit
	}
	pages := total / limit

	if total%limit > 0 {
		pages++
	}

	return pages
}

func CurrentPage(offset int, limit int) int {
	if limit == 0 {
		return 0
	}

	return (offset + limit) / limit
}

func GetEnv(key string) string {
	// load .env file
	switch godotenv.Load() {
	case godotenv.Load("../.env"):
		log.Println("Error loading .env file")
	case godotenv.Load("../../.env"):
		log.Println("Error loading .env file")
	}
	return os.Getenv(key)
}

const charset = "abcdefghijklmnopqrstuvwxyz" +
	"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

var seededRand *rand.Rand = rand.New(
	rand.NewSource(time.Now().UnixNano()))

func StringWithCharset(length int, charset string) string {
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[seededRand.Intn(len(charset))]
	}
	return string(b)
}

func String(length int) string {
	return StringWithCharset(length, charset)
}

func RangeDate(start, end time.Time) func() time.Time {
	// utc := time.Now().UTC()
	// local := utc
	// location, err := time.LoadLocation("Asia/Jakarta")
	// if err == nil {
	// 	local = local.In(location)
	// }
	y, m, d := start.Date()
	start = time.Date(y, m, d, 0, 0, 0, 0, time.UTC)
	y, m, d = end.Date()
	end = time.Date(y, m, d, 1, 0, 0, 0, time.UTC)

	return func() time.Time {
		if start.After(end) {
			return time.Time{}
		}
		date := start
		start = start.AddDate(0, 0, 1)
		return date
	}
}

func DateEqual(date1, date2 time.Time) bool {
	y1, m1, d1 := date1.Date()
	y2, m2, d2 := date2.Date()
	return y1 == y2 && m1 == m2 && d1 == d2
}
