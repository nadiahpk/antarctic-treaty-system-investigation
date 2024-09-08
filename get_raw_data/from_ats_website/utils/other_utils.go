package utils

import (
	"log"
	"os"
)

func GetRawDataPath() string {
	path, exists := os.LookupEnv("DATA_RAW")
	if !exists {
		log.Fatalf("DATA_RAW path not found in environment variables. Check the .envrc.")
	}

	return path
}
