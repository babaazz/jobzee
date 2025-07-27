package config

import (
	"os"
	"strconv"
)

type Config struct {
	Environment      string
	Database         DatabaseConfig
	Redis            RedisConfig
	Kafka            KafkaConfig
	MinIO            MinIOConfig
	Auth             AuthConfig
	APIPort          int
	JobServicePort   int
	CandidateServicePort int
	AgentServicePort int
}

type DatabaseConfig struct {
	Host     string
	Port     string
	User     string
	Password string
	DBName   string
	SSLMode  string
}

type RedisConfig struct {
	Host     string
	Port     string
	Password string
	DB       int
}

type KafkaConfig struct {
	Brokers []string
	Topic   string
}

type MinIOConfig struct {
	Endpoint        string
	AccessKeyID     string
	SecretAccessKey string
	UseSSL          bool
	BucketName      string
}

type AuthConfig struct {
	JWTSecret        string
	JWTExpiration    int // in hours
	BCryptCost       int
	RefreshTokenExp  int // in days
}

func Load() *Config {
	return &Config{
		Environment: getEnv("ENVIRONMENT", "development"),
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnv("DB_PORT", "5432"),
			User:     getEnv("DB_USER", "postgres"),
			Password: getEnv("DB_PASSWORD", "password"),
			DBName:   getEnv("DB_NAME", "jobzee"),
			SSLMode:  getEnv("DB_SSLMODE", "disable"),
		},
		Redis: RedisConfig{
			Host:     getEnv("REDIS_HOST", "localhost"),
			Port:     getEnv("REDIS_PORT", "6379"),
			Password: getEnv("REDIS_PASSWORD", ""),
			DB:       0,
		},
		Kafka: KafkaConfig{
			Brokers: []string{getEnv("KAFKA_BROKERS", "localhost:9092")},
			Topic:   getEnv("KAFKA_TOPIC", "jobzee-events"),
		},
		MinIO: MinIOConfig{
			Endpoint:        getEnv("MINIO_ENDPOINT", "localhost:9000"),
			AccessKeyID:     getEnv("MINIO_ACCESS_KEY", "minioadmin"),
			SecretAccessKey: getEnv("MINIO_SECRET_KEY", "minioadmin"),
			UseSSL:          false,
			BucketName:      getEnv("MINIO_BUCKET", "jobzee"),
		},
		Auth: AuthConfig{
			JWTSecret:       getEnv("JWT_SECRET", "your-secret-key-change-in-production"),
			JWTExpiration:   getEnvAsInt("JWT_EXPIRATION", 24), // 24 hours
			BCryptCost:      getEnvAsInt("BCRYPT_COST", 12),
			RefreshTokenExp: getEnvAsInt("REFRESH_TOKEN_EXP", 7), // 7 days
		},
		APIPort:           getEnvAsInt("API_PORT", 8080),
		JobServicePort:    getEnvAsInt("JOB_SERVICE_PORT", 8081),
		CandidateServicePort: getEnvAsInt("CANDIDATE_SERVICE_PORT", 8082),
		AgentServicePort:  getEnvAsInt("AGENT_SERVICE_PORT", 8083),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
} 