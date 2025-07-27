package repository

import (
	"github.com/jobzee/multi-agent-backend/internal/models"
	"gorm.io/gorm"
)

// UserRepositoryInterface defines the interface for user repository operations
type UserRepositoryInterface interface {
	Create(user *models.User) error
	GetByID(id uint) (*models.User, error)
	GetByEmail(email string) (*models.User, error)
	Update(user *models.User) error
	Delete(id uint) error
	List(offset, limit int) ([]models.User, error)
	GetByRole(role models.UserRole) ([]models.User, error)
	GetActiveUsers() ([]models.User, error)
	SearchUsers(query string) ([]models.User, error)
	GetUsersByCompany(companyID uint) ([]models.User, error)
	CountUsers() (int64, error)
	GetUserWithProfile(userID uint) (*models.User, error)
	GetUserWithJobs(userID uint) (*models.User, error)
	GetUserWithApplications(userID uint) (*models.User, error)
}

type UserRepository struct {
	db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
	return &UserRepository{db: db}
}

// Create creates a new user
func (r *UserRepository) Create(user *models.User) error {
	return r.db.Create(user).Error
}

// GetByID retrieves a user by ID
func (r *UserRepository) GetByID(id uint) (*models.User, error) {
	var user models.User
	err := r.db.First(&user, id).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetByEmail retrieves a user by email
func (r *UserRepository) GetByEmail(email string) (*models.User, error) {
	var user models.User
	err := r.db.Where("email = ?", email).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// Update updates a user
func (r *UserRepository) Update(user *models.User) error {
	return r.db.Save(user).Error
}

// Delete deletes a user
func (r *UserRepository) Delete(id uint) error {
	return r.db.Delete(&models.User{}, id).Error
}

// List retrieves all users with pagination
func (r *UserRepository) List(offset, limit int) ([]models.User, error) {
	var users []models.User
	err := r.db.Offset(offset).Limit(limit).Find(&users).Error
	return users, err
}

// GetByRole retrieves users by role
func (r *UserRepository) GetByRole(role models.UserRole) ([]models.User, error) {
	var users []models.User
	err := r.db.Where("role = ?", role).Find(&users).Error
	return users, err
}

// GetActiveUsers retrieves all active users
func (r *UserRepository) GetActiveUsers() ([]models.User, error) {
	var users []models.User
	err := r.db.Where("is_active = ?", true).Find(&users).Error
	return users, err
}

// SearchUsers searches users by name or email
func (r *UserRepository) SearchUsers(query string) ([]models.User, error) {
	var users []models.User
	err := r.db.Where("first_name ILIKE ? OR last_name ILIKE ? OR email ILIKE ?", 
		"%"+query+"%", "%"+query+"%", "%"+query+"%").Find(&users).Error
	return users, err
}

// GetUsersByCompany retrieves users by company ID
func (r *UserRepository) GetUsersByCompany(companyID uint) ([]models.User, error) {
	var users []models.User
	err := r.db.Where("company_id = ?", companyID).Find(&users).Error
	return users, err
}

// CountUsers counts total number of users
func (r *UserRepository) CountUsers() (int64, error) {
	var count int64
	err := r.db.Model(&models.User{}).Count(&count).Error
	return count, err
}

// GetUserWithProfile retrieves a user with their candidate profile
func (r *UserRepository) GetUserWithProfile(userID uint) (*models.User, error) {
	var user models.User
	err := r.db.Preload("CandidateProfile").First(&user, userID).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetUserWithJobs retrieves a user with their created jobs
func (r *UserRepository) GetUserWithJobs(userID uint) (*models.User, error) {
	var user models.User
	err := r.db.Preload("Jobs").First(&user, userID).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetUserWithApplications retrieves a user with their applications
func (r *UserRepository) GetUserWithApplications(userID uint) (*models.User, error) {
	var user models.User
	err := r.db.Preload("Applications").Preload("Applications.Job").First(&user, userID).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
} 