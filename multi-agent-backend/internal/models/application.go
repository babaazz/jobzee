package models

import (
	"time"

	"gorm.io/gorm"
)

// ApplicationStatus represents the status of a job application
type ApplicationStatus string

const (
	StatusApplied    ApplicationStatus = "applied"
	StatusReviewing  ApplicationStatus = "reviewing"
	StatusInterview  ApplicationStatus = "interview"
	StatusRejected   ApplicationStatus = "rejected"
	StatusAccepted   ApplicationStatus = "accepted"
	StatusWithdrawn  ApplicationStatus = "withdrawn"
)

// Application represents a job application
type Application struct {
	ID              string             `json:"id" gorm:"primaryKey;type:uuid;default:gen_random_uuid()"`
	UserID          uint               `json:"user_id" gorm:"not null"`
	JobID           string             `json:"job_id" gorm:"not null"`
	Status          ApplicationStatus  `json:"status" gorm:"default:'applied'"`
	CoverLetter     *string            `json:"cover_letter,omitempty"`
	ResumeURL       *string            `json:"resume_url,omitempty"`
	PortfolioURL    *string            `json:"portfolio_url,omitempty"`
	GitHubURL       *string            `json:"github_url,omitempty"`
	LinkedInURL     *string            `json:"linkedin_url,omitempty"`
	AppliedAt       time.Time          `json:"applied_at"`
	UpdatedAt       time.Time          `json:"updated_at"`
	DeletedAt       gorm.DeletedAt     `json:"deleted_at,omitempty" gorm:"index"`
	
	// Interview information
	InterviewDate   *time.Time         `json:"interview_date,omitempty"`
	InterviewType   *string            `json:"interview_type,omitempty"` // phone, video, onsite
	InterviewNotes  *string            `json:"interview_notes,omitempty"`
	
	// Agent feedback
	AgentFeedback   *string            `json:"agent_feedback,omitempty"`
	MatchScore      *float64           `json:"match_score,omitempty"`
	
	// Relationships
	User            User               `json:"user,omitempty" gorm:"foreignKey:UserID"`
	Job             Job                `json:"job,omitempty" gorm:"foreignKey:JobID"`
}

// CreateApplicationRequest represents a request to create an application
type CreateApplicationRequest struct {
	JobID        string  `json:"job_id" binding:"required"`
	CoverLetter  *string `json:"cover_letter,omitempty"`
	ResumeURL    *string `json:"resume_url,omitempty"`
	PortfolioURL *string `json:"portfolio_url,omitempty"`
	GitHubURL    *string `json:"github_url,omitempty"`
	LinkedInURL  *string `json:"linkedin_url,omitempty"`
}

// UpdateApplicationRequest represents a request to update an application
type UpdateApplicationRequest struct {
	Status         *ApplicationStatus `json:"status,omitempty"`
	CoverLetter    *string            `json:"cover_letter,omitempty"`
	ResumeURL      *string            `json:"resume_url,omitempty"`
	PortfolioURL   *string            `json:"portfolio_url,omitempty"`
	GitHubURL      *string            `json:"github_url,omitempty"`
	LinkedInURL    *string            `json:"linkedin_url,omitempty"`
	InterviewDate  *time.Time         `json:"interview_date,omitempty"`
	InterviewType  *string            `json:"interview_type,omitempty"`
	InterviewNotes *string            `json:"interview_notes,omitempty"`
	AgentFeedback  *string            `json:"agent_feedback,omitempty"`
	MatchScore     *float64           `json:"match_score,omitempty"`
}

// ApplicationResponse represents an application response
type ApplicationResponse struct {
	Application *Application `json:"application"`
	Job         *Job         `json:"job,omitempty"`
	User        *User        `json:"user,omitempty"`
}

// TableName specifies the table name for Application
func (Application) TableName() string {
	return "applications"
} 