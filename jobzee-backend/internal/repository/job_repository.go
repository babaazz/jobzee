package repository

import (
	"context"
	"errors"

	"github.com/jobzee/jobzee-backend/internal/models"
	"gorm.io/gorm"
)

type JobRepository struct {
	db *gorm.DB
}

func NewJobRepository(db *gorm.DB) *JobRepository {
	return &JobRepository{db: db}
}

func (r *JobRepository) Create(ctx context.Context, job *models.Job) (*models.Job, error) {
	if err := r.db.WithContext(ctx).Create(job).Error; err != nil {
		return nil, err
	}
	return job, nil
}

func (r *JobRepository) GetAll(ctx context.Context) ([]*models.Job, error) {
	var jobs []*models.Job
	if err := r.db.WithContext(ctx).Find(&jobs).Error; err != nil {
		return nil, err
	}
	return jobs, nil
}

func (r *JobRepository) GetByID(ctx context.Context, id string) (*models.Job, error) {
	var job models.Job
	if err := r.db.WithContext(ctx).Where("id = ?", id).First(&job).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("job not found")
		}
		return nil, err
	}
	return &job, nil
}

func (r *JobRepository) Update(ctx context.Context, job *models.Job) (*models.Job, error) {
	if err := r.db.WithContext(ctx).Save(job).Error; err != nil {
		return nil, err
	}
	return job, nil
}

func (r *JobRepository) Delete(ctx context.Context, id string) error {
	return r.db.WithContext(ctx).Delete(&models.Job{}, "id = ?", id).Error
}

func (r *JobRepository) Search(ctx context.Context, query string, location string, skills []string) ([]*models.Job, error) {
	var jobs []*models.Job
	db := r.db.WithContext(ctx)

	if query != "" {
		db = db.Where("title ILIKE ? OR description ILIKE ?", "%"+query+"%", "%"+query+"%")
	}

	if location != "" {
		db = db.Where("location ILIKE ?", "%"+location+"%")
	}

	if len(skills) > 0 {
		db = db.Where("skills && ?", skills)
	}

	if err := db.Find(&jobs).Error; err != nil {
		return nil, err
	}

	return jobs, nil
} 