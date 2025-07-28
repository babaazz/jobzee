package repository

import (
	"context"
	"errors"

	"github.com/jobzee/jobzee-backend/internal/models"
	"gorm.io/gorm"
)

type CandidateRepository struct {
	db *gorm.DB
}

func NewCandidateRepository(db *gorm.DB) *CandidateRepository {
	return &CandidateRepository{db: db}
}

func (r *CandidateRepository) Create(ctx context.Context, candidate *models.Candidate) (*models.Candidate, error) {
	if err := r.db.WithContext(ctx).Create(candidate).Error; err != nil {
		return nil, err
	}
	return candidate, nil
}

func (r *CandidateRepository) GetAll(ctx context.Context) ([]*models.Candidate, error) {
	var candidates []*models.Candidate
	if err := r.db.WithContext(ctx).Find(&candidates).Error; err != nil {
		return nil, err
	}
	return candidates, nil
}

func (r *CandidateRepository) GetByID(ctx context.Context, id string) (*models.Candidate, error) {
	var candidate models.Candidate
	if err := r.db.WithContext(ctx).Where("id = ?", id).First(&candidate).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("candidate not found")
		}
		return nil, err
	}
	return &candidate, nil
}

func (r *CandidateRepository) Update(ctx context.Context, candidate *models.Candidate) (*models.Candidate, error) {
	if err := r.db.WithContext(ctx).Save(candidate).Error; err != nil {
		return nil, err
	}
	return candidate, nil
}

func (r *CandidateRepository) Delete(ctx context.Context, id string) error {
	return r.db.WithContext(ctx).Delete(&models.Candidate{}, "id = ?", id).Error
}

func (r *CandidateRepository) Search(ctx context.Context, query string, location string, skills []string) ([]*models.Candidate, error) {
	var candidates []*models.Candidate
	db := r.db.WithContext(ctx)

	if query != "" {
		db = db.Where("name ILIKE ? OR email ILIKE ?", "%"+query+"%", "%"+query+"%")
	}

	if location != "" {
		db = db.Where("location ILIKE ?", "%"+location+"%")
	}

	if len(skills) > 0 {
		db = db.Where("skills && ?", skills)
	}

	if err := db.Find(&candidates).Error; err != nil {
		return nil, err
	}

	return candidates, nil
} 