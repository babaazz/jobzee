package services

import (
	"context"

	"github.com/jobzee/multi-agent-backend/internal/config"
	"github.com/jobzee/multi-agent-backend/internal/models"
	"github.com/jobzee/multi-agent-backend/internal/repository"
)

type JobService struct {
	config     *config.Config
	repository *repository.JobRepository
}

func NewJobService(cfg *config.Config, repo *repository.JobRepository) *JobService {
	return &JobService{
		config:     cfg,
		repository: repo,
	}
}

func (s *JobService) CreateJob(ctx context.Context, job *models.Job) (*models.Job, error) {
	return s.repository.Create(ctx, job)
}

func (s *JobService) GetJobs(ctx context.Context) ([]*models.Job, error) {
	return s.repository.GetAll(ctx)
}

func (s *JobService) GetJob(ctx context.Context, id string) (*models.Job, error) {
	return s.repository.GetByID(ctx, id)
}

func (s *JobService) UpdateJob(ctx context.Context, job *models.Job) (*models.Job, error) {
	return s.repository.Update(ctx, job)
}

func (s *JobService) DeleteJob(ctx context.Context, id string) error {
	return s.repository.Delete(ctx, id)
}

func (s *JobService) SearchJobs(ctx context.Context, query string, location string, skills []string) ([]*models.Job, error) {
	return s.repository.Search(ctx, query, location, skills)
} 