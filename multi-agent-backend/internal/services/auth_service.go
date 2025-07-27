package services

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/jobzee/multi-agent-backend/internal/config"
	"github.com/jobzee/multi-agent-backend/internal/models"
	"github.com/jobzee/multi-agent-backend/internal/repository"
	"golang.org/x/crypto/bcrypt"
)

type AuthService struct {
	config     *config.Config
	userRepo   *repository.UserRepository
}

func NewAuthService(cfg *config.Config, userRepo *repository.UserRepository) *AuthService {
	return &AuthService{
		config:   cfg,
		userRepo: userRepo,
	}
}

// Register creates a new user account
func (s *AuthService) Register(req *models.RegisterRequest) (*models.AuthResponse, error) {
	// Check if user already exists
	existingUser, err := s.userRepo.GetByEmail(req.Email)
	if err == nil && existingUser != nil {
		return nil, errors.New("user already exists")
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), s.config.Auth.BCryptCost)
	if err != nil {
		return nil, fmt.Errorf("failed to hash password: %w", err)
	}

	// Create user
	user := &models.User{
		Email:     req.Email,
		Password:  string(hashedPassword),
		FirstName: req.FirstName,
		LastName:  req.LastName,
		Role:      req.Role,
		Phone:     req.Phone,
		Location:  req.Location,
		CompanyID: req.CompanyID,
	}

	if err := s.userRepo.Create(user); err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	// Generate tokens
	accessToken, refreshToken, err := s.generateTokens(user)
	if err != nil {
		return nil, fmt.Errorf("failed to generate tokens: %w", err)
	}

	return &models.AuthResponse{
		User:         user,
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresIn:    int64(s.config.Auth.JWTExpiration * 3600), // Convert hours to seconds
	}, nil
}

// Login authenticates a user and returns tokens
func (s *AuthService) Login(req *models.LoginRequest) (*models.AuthResponse, error) {
	// Get user by email
	user, err := s.userRepo.GetByEmail(req.Email)
	if err != nil {
		return nil, errors.New("invalid credentials")
	}

	// Check if user is active
	if !user.IsActive {
		return nil, errors.New("account is deactivated")
	}

	// Verify password
	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		return nil, errors.New("invalid credentials")
	}

	// Update last login
	now := time.Now()
	user.LastLoginAt = &now
	if err := s.userRepo.Update(user); err != nil {
		// Log error but don't fail login
		fmt.Printf("Failed to update last login: %v\n", err)
	}

	// Generate tokens
	accessToken, refreshToken, err := s.generateTokens(user)
	if err != nil {
		return nil, fmt.Errorf("failed to generate tokens: %w", err)
	}

	return &models.AuthResponse{
		User:         user,
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresIn:    int64(s.config.Auth.JWTExpiration * 3600), // Convert hours to seconds
	}, nil
}

// RefreshToken generates new access token using refresh token
func (s *AuthService) RefreshToken(refreshToken string) (*models.AuthResponse, error) {
	// Parse and validate refresh token
	claims, err := s.parseToken(refreshToken)
	if err != nil {
		return nil, errors.New("invalid refresh token")
	}

	// Get user
	user, err := s.userRepo.GetByID(claims.UserID)
	if err != nil {
		return nil, errors.New("user not found")
	}

	// Check if user is active
	if !user.IsActive {
		return nil, errors.New("account is deactivated")
	}

	// Generate new tokens
	accessToken, newRefreshToken, err := s.generateTokens(user)
	if err != nil {
		return nil, fmt.Errorf("failed to generate tokens: %w", err)
	}

	return &models.AuthResponse{
		User:         user,
		AccessToken:  accessToken,
		RefreshToken: newRefreshToken,
		ExpiresIn:    int64(s.config.Auth.JWTExpiration * 3600), // Convert hours to seconds
	}, nil
}

// ValidateToken validates an access token and returns user claims
func (s *AuthService) ValidateToken(tokenString string) (*models.Claims, error) {
	claims, err := s.parseToken(tokenString)
	if err != nil {
		return nil, err
	}

	// Check if token is expired
	if time.Now().Unix() > claims.Exp {
		return nil, errors.New("token expired")
	}

	// Verify user still exists and is active
	user, err := s.userRepo.GetByID(claims.UserID)
	if err != nil {
		return nil, errors.New("user not found")
	}

	if !user.IsActive {
		return nil, errors.New("user account is deactivated")
	}

	return claims, nil
}

// ChangePassword changes user password
func (s *AuthService) ChangePassword(userID uint, req *models.ChangePasswordRequest) error {
	user, err := s.userRepo.GetByID(userID)
	if err != nil {
		return errors.New("user not found")
	}

	// Verify current password
	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.CurrentPassword)); err != nil {
		return errors.New("current password is incorrect")
	}

	// Hash new password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.NewPassword), s.config.Auth.BCryptCost)
	if err != nil {
		return fmt.Errorf("failed to hash password: %w", err)
	}

	// Update password
	user.Password = string(hashedPassword)
	return s.userRepo.Update(user)
}

// UpdateProfile updates user profile
func (s *AuthService) UpdateProfile(userID uint, req *models.UpdateProfileRequest) (*models.User, error) {
	user, err := s.userRepo.GetByID(userID)
	if err != nil {
		return nil, errors.New("user not found")
	}

	// Update fields if provided
	if req.FirstName != nil {
		user.FirstName = *req.FirstName
	}
	if req.LastName != nil {
		user.LastName = *req.LastName
	}
	if req.Phone != nil {
		user.Phone = req.Phone
	}
	if req.Location != nil {
		user.Location = req.Location
	}
	if req.Bio != nil {
		user.Bio = req.Bio
	}
	if req.ProfilePictureURL != nil {
		user.ProfilePictureURL = req.ProfilePictureURL
	}
	if req.CompanyName != nil {
		user.CompanyName = req.CompanyName
	}
	if req.JobTitle != nil {
		user.JobTitle = req.JobTitle
	}

	if err := s.userRepo.Update(user); err != nil {
		return nil, fmt.Errorf("failed to update profile: %w", err)
	}

	return user, nil
}

// generateTokens generates access and refresh tokens
func (s *AuthService) generateTokens(user *models.User) (string, string, error) {
	// Generate access token
	accessToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": user.ID,
		"email":   user.Email,
		"role":    user.Role,
		"exp":     time.Now().Add(time.Duration(s.config.Auth.JWTExpiration) * time.Hour).Unix(),
		"iat":     time.Now().Unix(),
		"type":    "access",
	})

	accessTokenString, err := accessToken.SignedString([]byte(s.config.Auth.JWTSecret))
	if err != nil {
		return "", "", err
	}

	// Generate refresh token
	refreshToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": user.ID,
		"email":   user.Email,
		"role":    user.Role,
		"exp":     time.Now().Add(time.Duration(s.config.Auth.RefreshTokenExp*24) * time.Hour).Unix(),
		"iat":     time.Now().Unix(),
		"type":    "refresh",
	})

	refreshTokenString, err := refreshToken.SignedString([]byte(s.config.Auth.JWTSecret))
	if err != nil {
		return "", "", err
	}

	return accessTokenString, refreshTokenString, nil
}

// parseToken parses and validates a JWT token
func (s *AuthService) parseToken(tokenString string) (*models.Claims, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(s.config.Auth.JWTSecret), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		userID := uint(claims["user_id"].(float64))
		email := claims["email"].(string)
		role := models.UserRole(claims["role"].(string))
		exp := int64(claims["exp"].(float64))

		return &models.Claims{
			UserID: userID,
			Email:  email,
			Role:   role,
			Exp:    exp,
		}, nil
	}

	return nil, errors.New("invalid token")
}

// generateRandomToken generates a random token for password reset
func (s *AuthService) generateRandomToken() (string, error) {
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}
	return hex.EncodeToString(bytes), nil
} 