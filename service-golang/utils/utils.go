package utils

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

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

	body := map[string]string{
		"error": message,
	}
	json.NewEncoder(w).Encode(body)
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
