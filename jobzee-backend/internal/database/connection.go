package database

import (
	"fmt"
	"log"

	"github.com/jobzee/jobzee-backend/internal/config"
	"github.com/jobzee/jobzee-backend/internal/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// Connection represents a database connection
type Connection struct {
	DB *gorm.DB
}

// NewConnection creates a new database connection
func NewConnection(cfg config.DatabaseConfig) (*Connection, error) {
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		cfg.Host,
		cfg.Port,
		cfg.User,
		cfg.Password,
		cfg.DBName,
		cfg.SSLMode,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Auto migrate models
	if err := db.AutoMigrate(
		&models.User{},
		&models.Job{},
		&models.Candidate{},
		&models.Application{},
	); err != nil {
		return nil, fmt.Errorf("failed to migrate database: %w", err)
	}

	log.Println("Database connected and migrated successfully")
	return &Connection{DB: db}, nil
}

// Close closes the database connection
func (c *Connection) Close() error {
	sqlDB, err := c.DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

// GetDB returns the underlying GORM DB instance
func (c *Connection) GetDB() *gorm.DB {
	return c.DB
} 