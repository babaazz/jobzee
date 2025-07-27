package services

import (
	"context"

	"github.com/jobzee/multi-agent-backend/internal/config"
	"github.com/jobzee/multi-agent-backend/internal/models"
	"github.com/jobzee/multi-agent-backend/internal/repository"
)

type CandidateService struct {
	config     *config.Config
	repository *repository.CandidateRepository
}

func NewCandidateService(cfg *config.Config, repo *repository.CandidateRepository) *CandidateService {
	return &CandidateService{
		config:     cfg,
		repository: repo,
	}
}

func (s *CandidateService) CreateCandidate(ctx context.Context, candidate *models.Candidate) (*models.Candidate, error) {
	return s.repository.Create(ctx, candidate)
}

func (s *CandidateService) GetCandidates(ctx context.Context) ([]*models.Candidate, error) {
	return s.repository.GetAll(ctx)
}

func (s *CandidateService) GetCandidate(ctx context.Context, id string) (*models.Candidate, error) {
	return s.repository.GetByID(ctx, id)
}

func (s *CandidateService) UpdateCandidate(ctx context.Context, candidate *models.Candidate) (*models.Candidate, error) {
	return s.repository.Update(ctx, candidate)
}

func (s *CandidateService) DeleteCandidate(ctx context.Context, id string) error {
	return s.repository.Delete(ctx, id)
}

func (s *CandidateService) SearchCandidates(ctx context.Context, query string, location string, skills []string) ([]*models.Candidate, error) {
	return s.repository.Search(ctx, query, location, skills)
} 