package services

import (
	"testing"

	"github.com/jobzee/jobzee-backend/internal/config"
	"github.com/jobzee/jobzee-backend/internal/models"
	"github.com/jobzee/jobzee-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

// MockUserRepository is a mock implementation of UserRepositoryInterface
type MockUserRepository struct {
	mock.Mock
}

// Ensure MockUserRepository implements UserRepositoryInterface
var _ repository.UserRepositoryInterface = (*MockUserRepository)(nil)

func (m *MockUserRepository) Create(user *models.User) error {
	args := m.Called(user)
	return args.Error(0)
}

func (m *MockUserRepository) GetByID(id uint) (*models.User, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) GetByEmail(email string) (*models.User, error) {
	args := m.Called(email)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) Update(user *models.User) error {
	args := m.Called(user)
	return args.Error(0)
}

func (m *MockUserRepository) Delete(id uint) error {
	args := m.Called(id)
	return args.Error(0)
}

func (m *MockUserRepository) List(offset, limit int) ([]models.User, error) {
	args := m.Called(offset, limit)
	return args.Get(0).([]models.User), args.Error(1)
}

func (m *MockUserRepository) GetByRole(role models.UserRole) ([]models.User, error) {
	args := m.Called(role)
	return args.Get(0).([]models.User), args.Error(1)
}

func (m *MockUserRepository) GetActiveUsers() ([]models.User, error) {
	args := m.Called()
	return args.Get(0).([]models.User), args.Error(1)
}

func (m *MockUserRepository) SearchUsers(query string) ([]models.User, error) {
	args := m.Called(query)
	return args.Get(0).([]models.User), args.Error(1)
}

func (m *MockUserRepository) GetUsersByCompany(companyID uint) ([]models.User, error) {
	args := m.Called(companyID)
	return args.Get(0).([]models.User), args.Error(1)
}

func (m *MockUserRepository) CountUsers() (int64, error) {
	args := m.Called()
	return args.Get(0).(int64), args.Error(1)
}

func (m *MockUserRepository) GetUserWithProfile(userID uint) (*models.User, error) {
	args := m.Called(userID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) GetUserWithJobs(userID uint) (*models.User, error) {
	args := m.Called(userID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) GetUserWithApplications(userID uint) (*models.User, error) {
	args := m.Called(userID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func TestAuthService_Register(t *testing.T) {
	// Setup
	cfg := &config.Config{
		Auth: config.AuthConfig{
			JWTSecret:     "test-secret-key",
			JWTExpiration: 24,
			BCryptCost:    12,
		},
	}
	mockRepo := new(MockUserRepository)
	authService := NewAuthService(cfg, mockRepo)

	tests := []struct {
		name          string
		request       *models.RegisterRequest
		setupMock     func()
		expectedError bool
	}{
		{
			name: "Successful registration",
			request: &models.RegisterRequest{
				Email:     "test@example.com",
				Password:  "password123",
				FirstName: "John",
				LastName:  "Doe",
				Role:      models.RoleCandidate,
			},
			setupMock: func() {
				mockRepo.On("GetByEmail", "test@example.com").Return(nil, gorm.ErrRecordNotFound)
				mockRepo.On("Create", mock.AnythingOfType("*models.User")).Return(nil)
			},
			expectedError: false,
		},
		{
			name: "User already exists",
			request: &models.RegisterRequest{
				Email:     "existing@example.com",
				Password:  "password123",
				FirstName: "John",
				LastName:  "Doe",
				Role:      models.RoleCandidate,
			},
			setupMock: func() {
				existingUser := &models.User{Email: "existing@example.com"}
				mockRepo.On("GetByEmail", "existing@example.com").Return(existingUser, nil)
			},
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset mock before each test
			mockRepo.ExpectedCalls = nil
			tt.setupMock()

			response, err := authService.Register(tt.request)

			if tt.expectedError {
				assert.Error(t, err)
				assert.Nil(t, response)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, response)
				assert.NotEmpty(t, response.AccessToken)
				assert.NotEmpty(t, response.RefreshToken)
				assert.Equal(t, tt.request.Email, response.User.Email)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

func TestAuthService_Login(t *testing.T) {
	// Setup
	cfg := &config.Config{
		Auth: config.AuthConfig{
			JWTSecret:     "test-secret-key",
			JWTExpiration: 24,
			BCryptCost:    12,
		},
	}
	mockRepo := new(MockUserRepository)
	authService := NewAuthService(cfg, mockRepo)

	// Create a test user with hashed password
	hashedPassword, _ := authService.generateHashedPassword("password123")
	testUser := &models.User{
		ID:        1,
		Email:     "test@example.com",
		Password:  hashedPassword,
		FirstName: "John",
		LastName:  "Doe",
		Role:      models.RoleCandidate,
		IsActive:  true,
	}

	tests := []struct {
		name          string
		request       *models.LoginRequest
		setupMock     func()
		expectedError bool
	}{
		{
			name: "Successful login",
			request: &models.LoginRequest{
				Email:    "test@example.com",
				Password: "password123",
			},
			setupMock: func() {
				mockRepo.On("GetByEmail", "test@example.com").Return(testUser, nil)
				mockRepo.On("Update", mock.AnythingOfType("*models.User")).Return(nil)
			},
			expectedError: false,
		},
		{
			name: "Invalid credentials",
			request: &models.LoginRequest{
				Email:    "test@example.com",
				Password: "wrongpassword",
			},
			setupMock: func() {
				mockRepo.On("GetByEmail", "test@example.com").Return(testUser, nil)
			},
			expectedError: true,
		},
		{
			name: "User not found",
			request: &models.LoginRequest{
				Email:    "nonexistent@example.com",
				Password: "password123",
			},
			setupMock: func() {
				mockRepo.On("GetByEmail", "nonexistent@example.com").Return(nil, gorm.ErrRecordNotFound)
			},
			expectedError: true,
		},
		{
			name: "Inactive user",
			request: &models.LoginRequest{
				Email:    "inactive@example.com",
				Password: "password123",
			},
			setupMock: func() {
				inactiveUser := *testUser
				inactiveUser.Email = "inactive@example.com"
				inactiveUser.IsActive = false
				mockRepo.On("GetByEmail", "inactive@example.com").Return(&inactiveUser, nil)
			},
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset mock before each test
			mockRepo.ExpectedCalls = nil
			tt.setupMock()

			response, err := authService.Login(tt.request)

			if tt.expectedError {
				assert.Error(t, err)
				assert.Nil(t, response)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, response)
				assert.NotEmpty(t, response.AccessToken)
				assert.NotEmpty(t, response.RefreshToken)
				assert.Equal(t, tt.request.Email, response.User.Email)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

func TestAuthService_ValidateToken(t *testing.T) {
	// Setup
	cfg := &config.Config{
		Auth: config.AuthConfig{
			JWTSecret:     "test-secret-key",
			JWTExpiration: 24,
			BCryptCost:    12,
		},
	}
	mockRepo := new(MockUserRepository)
	authService := NewAuthService(cfg, mockRepo)

	// Create a test user
	testUser := &models.User{
		ID:        1,
		Email:     "test@example.com",
		FirstName: "John",
		LastName:  "Doe",
		Role:      models.RoleCandidate,
		IsActive:  true,
	}

	// Generate a valid token
	accessToken, _, _ := authService.generateTokens(testUser)

	tests := []struct {
		name          string
		token         string
		setupMock     func()
		expectedError bool
	}{
		{
			name:  "Valid token",
			token: accessToken,
			setupMock: func() {
				mockRepo.On("GetByID", uint(1)).Return(testUser, nil)
			},
			expectedError: false,
		},
		{
			name:          "Invalid token",
			token:         "invalid-token",
			setupMock:     func() {},
			expectedError: true,
		},
		{
			name:  "User not found",
			token: accessToken,
			setupMock: func() {
				mockRepo.On("GetByID", uint(1)).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedError: true,
		},
		{
			name:  "Inactive user",
			token: accessToken,
			setupMock: func() {
				inactiveUser := *testUser
				inactiveUser.IsActive = false
				mockRepo.On("GetByID", uint(1)).Return(&inactiveUser, nil)
			},
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset mock before each test
			mockRepo.ExpectedCalls = nil
			tt.setupMock()

			claims, err := authService.ValidateToken(tt.token)

			if tt.expectedError {
				assert.Error(t, err)
				assert.Nil(t, claims)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, claims)
				assert.Equal(t, testUser.ID, claims.UserID)
				assert.Equal(t, testUser.Email, claims.Email)
				assert.Equal(t, testUser.Role, claims.Role)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

func TestAuthService_ChangePassword(t *testing.T) {
	// Setup
	cfg := &config.Config{
		Auth: config.AuthConfig{
			JWTSecret:     "test-secret-key",
			JWTExpiration: 24,
			BCryptCost:    12,
		},
	}
	mockRepo := new(MockUserRepository)
	authService := NewAuthService(cfg, mockRepo)

	// Create a test user with hashed password
	hashedPassword, _ := authService.generateHashedPassword("oldpassword")
	testUser := &models.User{
		ID:        1,
		Email:     "test@example.com",
		Password:  hashedPassword,
		FirstName: "John",
		LastName:  "Doe",
		Role:      models.RoleCandidate,
		IsActive:  true,
	}

	tests := []struct {
		name          string
		userID        uint
		request       *models.ChangePasswordRequest
		setupMock     func()
		expectedError bool
	}{
		{
			name:   "Successful password change",
			userID: 1,
			request: &models.ChangePasswordRequest{
				CurrentPassword: "oldpassword",
				NewPassword:     "newpassword123",
			},
			setupMock: func() {
				mockRepo.On("GetByID", uint(1)).Return(testUser, nil)
				mockRepo.On("Update", mock.AnythingOfType("*models.User")).Return(nil)
			},
			expectedError: false,
		},
		{
			name:   "Wrong current password",
			userID: 1,
			request: &models.ChangePasswordRequest{
				CurrentPassword: "wrongpassword",
				NewPassword:     "newpassword123",
			},
			setupMock: func() {
				mockRepo.On("GetByID", uint(1)).Return(testUser, nil)
			},
			expectedError: true,
		},
		{
			name:   "User not found",
			userID: 999,
			request: &models.ChangePasswordRequest{
				CurrentPassword: "oldpassword",
				NewPassword:     "newpassword123",
			},
			setupMock: func() {
				mockRepo.On("GetByID", uint(999)).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset mock before each test
			mockRepo.ExpectedCalls = nil
			tt.setupMock()

			err := authService.ChangePassword(tt.userID, tt.request)

			if tt.expectedError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

// Helper function to generate hashed password for testing
func (s *AuthService) generateHashedPassword(password string) (string, error) {
	// This is a helper method for testing - in real implementation it would be private
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), s.config.Auth.BCryptCost)
	if err != nil {
		return "", err
	}
	return string(hashedPassword), nil
}

func TestAuthService_UpdateProfile(t *testing.T) {
	// Setup
	cfg := &config.Config{
		Auth: config.AuthConfig{
			JWTSecret:     "test-secret-key",
			JWTExpiration: 24,
			BCryptCost:    12,
		},
	}
	mockRepo := new(MockUserRepository)
	authService := NewAuthService(cfg, mockRepo)

	// Create a test user
	testUser := &models.User{
		ID:        1,
		Email:     "test@example.com",
		FirstName: "John",
		LastName:  "Doe",
		Role:      models.RoleCandidate,
		IsActive:  true,
	}

	tests := []struct {
		name          string
		userID        uint
		request       *models.UpdateProfileRequest
		setupMock     func()
		expectedError bool
	}{
		{
			name:   "Successful profile update",
			userID: 1,
			request: &models.UpdateProfileRequest{
				FirstName: stringPtr("Jane"),
				LastName:  stringPtr("Smith"),
				Phone:     stringPtr("+1234567890"),
			},
			setupMock: func() {
				mockRepo.On("GetByID", uint(1)).Return(testUser, nil)
				mockRepo.On("Update", mock.AnythingOfType("*models.User")).Return(nil)
			},
			expectedError: false,
		},
		{
			name:   "User not found",
			userID: 999,
			request: &models.UpdateProfileRequest{
				FirstName: stringPtr("Jane"),
			},
			setupMock: func() {
				mockRepo.On("GetByID", uint(999)).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset mock before each test
			mockRepo.ExpectedCalls = nil
			tt.setupMock()

			user, err := authService.UpdateProfile(tt.userID, tt.request)

			if tt.expectedError {
				assert.Error(t, err)
				assert.Nil(t, user)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, user)
				if tt.request.FirstName != nil {
					assert.Equal(t, *tt.request.FirstName, user.FirstName)
				}
				if tt.request.LastName != nil {
					assert.Equal(t, *tt.request.LastName, user.LastName)
				}
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

// Helper function to create string pointers
func stringPtr(s string) *string {
	return &s
} 