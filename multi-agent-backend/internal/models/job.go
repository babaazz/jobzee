package models

import (
	"time"

	"gorm.io/gorm"
)

type Job struct {
	ID              string         `json:"id" gorm:"primaryKey;type:uuid;default:gen_random_uuid()"`
	Title           string         `json:"title" gorm:"not null"`
	Company         string         `json:"company" gorm:"not null"`
	Location        string         `json:"location"`
	Description     string         `json:"description"`
	Requirements    []string       `json:"requirements" gorm:"type:text[]"`
	Skills          []string       `json:"skills" gorm:"type:text[]"`
	ExperienceLevel string         `json:"experience_level"`
	SalaryRange     string         `json:"salary_range"`
	JobType         string         `json:"job_type"` // full-time, part-time, contract, internship
	RemoteFriendly  bool           `json:"remote_friendly"`
	Status          string         `json:"status" gorm:"default:'active'"` // active, closed, draft
	CreatedAt       time.Time      `json:"created_at"`
	UpdatedAt       time.Time      `json:"updated_at"`
	DeletedAt       gorm.DeletedAt `json:"deleted_at,omitempty" gorm:"index"`
} 