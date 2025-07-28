package models

import (
	"time"

	"gorm.io/gorm"
)

// User represents a user in the system
type User struct {
	ID                uint           `json:"id" gorm:"primaryKey"`
	Email             string         `json:"email" gorm:"uniqueIndex;not null"`
	Password          string         `json:"-" gorm:"not null"` // "-" means don't include in JSON
	FirstName         string         `json:"first_name" gorm:"not null"`
	LastName          string         `json:"last_name" gorm:"not null"`
	Role              UserRole       `json:"role" gorm:"not null;default:'candidate'"`
	IsActive          bool           `json:"is_active" gorm:"default:true"`
	EmailVerified     bool           `json:"email_verified" gorm:"default:false"`
	LastLoginAt       *time.Time     `json:"last_login_at"`
	CreatedAt         time.Time      `json:"created_at"`
	UpdatedAt         time.Time      `json:"updated_at"`
	DeletedAt         gorm.DeletedAt `json:"deleted_at,omitempty" gorm:"index"`
	
	// Profile information
	Phone             *string        `json:"phone,omitempty"`
	Location          *string        `json:"location,omitempty"`
	Bio               *string        `json:"bio,omitempty"`
	ProfilePictureURL *string        `json:"profile_picture_url,omitempty"`
	
	// Company information (for HR users)
	CompanyID         *uint          `json:"company_id,omitempty"`
	CompanyName       *string        `json:"company_name,omitempty"`
	JobTitle          *string        `json:"job_title,omitempty"`
	
	// Relationships
	CandidateProfile  *Candidate     `json:"candidate_profile,omitempty" gorm:"foreignKey:UserID"`
	Jobs              []Job          `json:"jobs,omitempty" gorm:"foreignKey:CreatedBy"`
	Applications      []Application  `json:"applications,omitempty" gorm:"foreignKey:UserID"`
}

// UserRole represents the role of a user
type UserRole string

const (
	RoleCandidate UserRole = "candidate"
	RoleHR        UserRole = "hr"
	RoleAdmin     UserRole = "admin"
)

// LoginRequest represents a login request
type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
}

// RegisterRequest represents a registration request
type RegisterRequest struct {
	Email     string   `json:"email" binding:"required,email"`
	Password  string   `json:"password" binding:"required,min=6"`
	FirstName string   `json:"first_name" binding:"required"`
	LastName  string   `json:"last_name" binding:"required"`
	Role      UserRole `json:"role" binding:"required,oneof=candidate hr"`
	Phone     *string  `json:"phone,omitempty"`
	Location  *string  `json:"location,omitempty"`
	CompanyID *uint    `json:"company_id,omitempty"`
}

// AuthResponse represents an authentication response
type AuthResponse struct {
	User         *User  `json:"user"`
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int64  `json:"expires_in"`
}

// RefreshTokenRequest represents a refresh token request
type RefreshTokenRequest struct {
	RefreshToken string `json:"refresh_token" binding:"required"`
}

// ChangePasswordRequest represents a password change request
type ChangePasswordRequest struct {
	CurrentPassword string `json:"current_password" binding:"required"`
	NewPassword     string `json:"new_password" binding:"required,min=6"`
}

// ForgotPasswordRequest represents a forgot password request
type ForgotPasswordRequest struct {
	Email string `json:"email" binding:"required,email"`
}

// ResetPasswordRequest represents a password reset request
type ResetPasswordRequest struct {
	Token       string `json:"token" binding:"required"`
	NewPassword string `json:"new_password" binding:"required,min=6"`
}

// UpdateProfileRequest represents a profile update request
type UpdateProfileRequest struct {
	FirstName         *string `json:"first_name,omitempty"`
	LastName          *string `json:"last_name,omitempty"`
	Phone             *string `json:"phone,omitempty"`
	Location          *string `json:"location,omitempty"`
	Bio               *string `json:"bio,omitempty"`
	ProfilePictureURL *string `json:"profile_picture_url,omitempty"`
	CompanyName       *string `json:"company_name,omitempty"`
	JobTitle          *string `json:"job_title,omitempty"`
}

// Claims represents JWT claims
type Claims struct {
	UserID uint     `json:"user_id"`
	Email  string   `json:"email"`
	Role   UserRole `json:"role"`
	Exp    int64    `json:"exp"`
}

// TableName specifies the table name for User
func (User) TableName() string {
	return "users"
} 