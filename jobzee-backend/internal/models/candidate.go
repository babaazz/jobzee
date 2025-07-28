package models

import (
	"time"

	"gorm.io/gorm"
)

type Candidate struct {
	ID                string         `json:"id" gorm:"primaryKey;type:uuid;default:gen_random_uuid()"`
	Name              string         `json:"name" gorm:"not null"`
	Email             string         `json:"email" gorm:"not null;unique"`
	Phone             string         `json:"phone"`
	Location          string         `json:"location"`
	Skills            []string       `json:"skills" gorm:"type:text[]"`
	Experience        []string       `json:"experience" gorm:"type:text[]"`
	Education         []string       `json:"education" gorm:"type:text[]"`
	ExperienceYears   int            `json:"experience_years"`
	PreferredRoles    []string       `json:"preferred_roles" gorm:"type:text[]"`
	SalaryExpectation string         `json:"salary_expectation"`
	ResumeURL         string         `json:"resume_url"`
	Status            string         `json:"status" gorm:"default:'active'"` // active, inactive, hired
	CreatedAt         time.Time      `json:"created_at"`
	UpdatedAt         time.Time      `json:"updated_at"`
	DeletedAt         gorm.DeletedAt `json:"deleted_at,omitempty" gorm:"index"`
} 