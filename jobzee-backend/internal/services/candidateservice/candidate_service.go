package candidateservice

import (
	"context"
	"fmt"
	"time"

	"github.com/jobzee/jobzee-backend/internal/database"
	"github.com/jobzee/jobzee-backend/internal/models"
	pb "github.com/jobzee/jobzee-backend/proto/proto/candidate_service"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/timestamppb"
	"gorm.io/gorm"
)

type CandidateService struct {
	pb.UnimplementedCandidateServiceServer
	db *database.Connection
}

func NewCandidateService(db *database.Connection) *CandidateService {
	return &CandidateService{db: db}
}

func (s *CandidateService) CreateCandidate(ctx context.Context, req *pb.CreateCandidateRequest) (*pb.Candidate, error) {
	// Convert proto Experience to model Experience
	experience := make([]string, len(req.Experience))
	for i, exp := range req.Experience {
		experience[i] = fmt.Sprintf("%s at %s: %s", exp.Position, exp.Company, exp.Description)
	}

	// Convert proto Education to model Education
	education := make([]string, len(req.Education))
	for i, edu := range req.Education {
		education[i] = fmt.Sprintf("%s in %s from %s (Grade: %s)", edu.Degree, edu.FieldOfStudy, edu.Institution, edu.Grade)
	}

	candidate := &models.Candidate{
		Name:              req.Name,
		Phone:             req.Phone,
		Location:          req.Location,
		Skills:            req.Skills,
		Experience:        experience,
		Education:         education,
		ExperienceYears:   int(req.ExperienceYears),
		PreferredRoles:    req.PreferredRoles,
		SalaryExpectation: req.SalaryExpectation,
		Status:            "active",
		CreatedAt:         time.Now(),
		UpdatedAt:         time.Now(),
	}

	if err := s.db.DB.WithContext(ctx).Create(candidate).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to create candidate: %v", err)
	}

	return s.candidateModelToProto(candidate), nil
}

func (s *CandidateService) GetCandidate(ctx context.Context, req *pb.GetCandidateRequest) (*pb.Candidate, error) {
	var candidate models.Candidate
	if err := s.db.DB.WithContext(ctx).Where("id = ?", req.Id).First(&candidate).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, status.Errorf(codes.NotFound, "candidate not found")
		}
		return nil, status.Errorf(codes.Internal, "failed to get candidate: %v", err)
	}

	return s.candidateModelToProto(&candidate), nil
}

func (s *CandidateService) ListCandidates(ctx context.Context, req *pb.ListCandidatesRequest) (*pb.ListCandidatesResponse, error) {
	var candidates []models.Candidate
	query := s.db.DB.WithContext(ctx)

	// Apply filters
	if req.Location != "" {
		query = query.Where("location ILIKE ?", "%"+req.Location+"%")
	}
	if len(req.Skills) > 0 {
		query = query.Where("skills && ?", req.Skills)
	}
	if req.MinExperienceYears > 0 {
		query = query.Where("experience_years >= ?", req.MinExperienceYears)
	}
	if req.MaxExperienceYears > 0 {
		query = query.Where("experience_years <= ?", req.MaxExperienceYears)
	}

	// Get total count
	var total int64
	query.Model(&models.Candidate{}).Count(&total)

	// Apply pagination
	limit := int(req.PageSize)
	if limit == 0 {
		limit = 10
	}
	query = query.Limit(limit)

	if req.PageToken != "" {
		// Simple pagination - in production, you'd want to use cursor-based pagination
		query = query.Offset(limit)
	}

	if err := query.Find(&candidates).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to list candidates: %v", err)
	}

	// Convert to proto
	protoCandidates := make([]*pb.Candidate, len(candidates))
	for i, candidate := range candidates {
		protoCandidates[i] = s.candidateModelToProto(&candidate)
	}

	return &pb.ListCandidatesResponse{
		Candidates:   protoCandidates,
		TotalCount:   int32(total),
		NextPageToken: fmt.Sprintf("%d", len(protoCandidates)),
	}, nil
}

func (s *CandidateService) UpdateCandidate(ctx context.Context, req *pb.UpdateCandidateRequest) (*pb.Candidate, error) {
	var candidate models.Candidate
	if err := s.db.DB.WithContext(ctx).Where("id = ?", req.Id).First(&candidate).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, status.Errorf(codes.NotFound, "candidate not found")
		}
		return nil, status.Errorf(codes.Internal, "failed to get candidate: %v", err)
	}

	// Update fields
	if req.Candidate.Name != "" {
		candidate.Name = req.Candidate.Name
	}
	if req.Candidate.Phone != "" {
		candidate.Phone = req.Candidate.Phone
	}
	if req.Candidate.Location != "" {
		candidate.Location = req.Candidate.Location
	}
	if len(req.Candidate.Skills) > 0 {
		candidate.Skills = req.Candidate.Skills
	}
	if len(req.Candidate.Experience) > 0 {
		// Convert proto Experience to model Experience
		experience := make([]string, len(req.Candidate.Experience))
		for i, exp := range req.Candidate.Experience {
			experience[i] = fmt.Sprintf("%s at %s: %s", exp.Position, exp.Company, exp.Description)
		}
		candidate.Experience = experience
	}
	if len(req.Candidate.Education) > 0 {
		// Convert proto Education to model Education
		education := make([]string, len(req.Candidate.Education))
		for i, edu := range req.Candidate.Education {
			education[i] = fmt.Sprintf("%s in %s from %s (Grade: %s)", edu.Degree, edu.FieldOfStudy, edu.Institution, edu.Grade)
		}
		candidate.Education = education
	}
	if req.Candidate.ExperienceYears > 0 {
		candidate.ExperienceYears = int(req.Candidate.ExperienceYears)
	}
	if len(req.Candidate.PreferredRoles) > 0 {
		candidate.PreferredRoles = req.Candidate.PreferredRoles
	}
	if req.Candidate.SalaryExpectation != "" {
		candidate.SalaryExpectation = req.Candidate.SalaryExpectation
	}
	if req.Candidate.Status != "" {
		candidate.Status = req.Candidate.Status
	}
	candidate.UpdatedAt = time.Now()

	if err := s.db.DB.WithContext(ctx).Save(&candidate).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to update candidate: %v", err)
	}

	return s.candidateModelToProto(&candidate), nil
}

func (s *CandidateService) DeleteCandidate(ctx context.Context, req *pb.DeleteCandidateRequest) (*emptypb.Empty, error) {
	if err := s.db.DB.WithContext(ctx).Delete(&models.Candidate{}, "id = ?", req.Id).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to delete candidate: %v", err)
	}

	return &emptypb.Empty{}, nil
}

func (s *CandidateService) SearchCandidates(ctx context.Context, req *pb.SearchCandidatesRequest) (*pb.SearchCandidatesResponse, error) {
	var candidates []models.Candidate
	query := s.db.DB.WithContext(ctx)

	// Apply search criteria
	if req.Query != "" {
		query = query.Where("name ILIKE ? OR email ILIKE ?", "%"+req.Query+"%", "%"+req.Query+"%")
	}
	if len(req.Skills) > 0 {
		query = query.Where("skills && ?", req.Skills)
	}
	if req.Location != "" {
		query = query.Where("location ILIKE ?", "%"+req.Location+"%")
	}
	if req.MinExperienceYears > 0 {
		query = query.Where("experience_years >= ?", req.MinExperienceYears)
	}
	if req.MaxExperienceYears > 0 {
		query = query.Where("experience_years <= ?", req.MaxExperienceYears)
	}
	if len(req.PreferredRoles) > 0 {
		query = query.Where("preferred_roles && ?", req.PreferredRoles)
	}
	if req.SalaryRange != "" {
		query = query.Where("salary_expectation = ?", req.SalaryRange)
	}

	// Get total count
	var total int64
	query.Model(&models.Candidate{}).Count(&total)

	// Apply pagination
	limit := int(req.PageSize)
	if limit == 0 {
		limit = 10
	}
	query = query.Limit(limit)

	if req.PageToken != "" {
		query = query.Offset(limit)
	}

	if err := query.Find(&candidates).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to search candidates: %v", err)
	}

	// Convert to proto
	protoCandidates := make([]*pb.Candidate, len(candidates))
	relevanceScores := make([]float32, len(candidates))
	for i, candidate := range candidates {
		protoCandidates[i] = s.candidateModelToProto(&candidate)
		relevanceScores[i] = 0.8 // Placeholder score - in production, calculate based on search relevance
	}

	return &pb.SearchCandidatesResponse{
		Candidates:     protoCandidates,
		TotalCount:     int32(total),
		NextPageToken:  fmt.Sprintf("%d", len(protoCandidates)),
		RelevanceScores: relevanceScores,
	}, nil
}

func (s *CandidateService) GetCandidateStats(ctx context.Context, req *pb.GetCandidateStatsRequest) (*pb.CandidateStats, error) {
	query := s.db.DB.WithContext(ctx)

	// Apply filters
	if req.Location != "" {
		query = query.Where("location = ?", req.Location)
	}
	if len(req.Skills) > 0 {
		query = query.Where("skills && ?", req.Skills)
	}

	// Get basic stats
	var totalCandidates, activeCandidates int64
	query.Model(&models.Candidate{}).Count(&totalCandidates)
	query.Where("status = ?", "active").Count(&activeCandidates)

	// Get candidates by location
	var locationStats []struct {
		Location string
		Count    int64
	}
	query.Model(&models.Candidate{}).
		Select("location, count(*) as count").
		Group("location").
		Scan(&locationStats)

	locationMap := make(map[string]int32)
	for _, stat := range locationStats {
		locationMap[stat.Location] = int32(stat.Count)
	}

	// Get candidates by experience level
	var experienceStats []struct {
		ExperienceYears int
		Count           int64
	}
	query.Model(&models.Candidate{}).
		Select("experience_years, count(*) as count").
		Group("experience_years").
		Scan(&experienceStats)

	experienceMap := make(map[string]int32)
	for _, stat := range experienceStats {
		level := "entry"
		if stat.ExperienceYears >= 5 {
			level = "senior"
		} else if stat.ExperienceYears >= 2 {
			level = "mid"
		}
		experienceMap[level] = int32(stat.Count)
	}

	// Calculate average experience years
	var avgExperience float64
	query.Model(&models.Candidate{}).
		Select("AVG(experience_years)").
		Scan(&avgExperience)

	return &pb.CandidateStats{
		TotalCandidates:           int32(totalCandidates),
		ActiveCandidates:          int32(activeCandidates),
		CandidatesByLocation:      locationMap,
		CandidatesByExperienceLevel: experienceMap,
		TopSkills:                 []string{}, // TODO: Implement top skills calculation
		TopPreferredRoles:         []string{}, // TODO: Implement top preferred roles calculation
		AverageExperienceYears:    float32(avgExperience),
		LastUpdated:               timestamppb.Now(),
	}, nil
}

// Helper function to convert model to proto
func (s *CandidateService) candidateModelToProto(candidate *models.Candidate) *pb.Candidate {
	// Convert model Experience to proto Experience
	experience := make([]*pb.Experience, len(candidate.Experience))
	for i, exp := range candidate.Experience {
		// Simple parsing - in production, you'd want to store this in a structured way
		experience[i] = &pb.Experience{
			Company:     "Unknown", // Would need to parse from string
			Position:    "Unknown", // Would need to parse from string
			Description: exp,
		}
	}

	// Convert model Education to proto Education
	education := make([]*pb.Education, len(candidate.Education))
	for i := range candidate.Education {
		// Simple parsing - in production, you'd want to store this in a structured way
		education[i] = &pb.Education{
			Institution:   "Unknown", // Would need to parse from string
			Degree:        "Unknown", // Would need to parse from string
			FieldOfStudy:  "Unknown", // Would need to parse from string
			Grade:         "Unknown", // Would need to parse from string
		}
	}

	return &pb.Candidate{
		Id:                candidate.ID,
		Name:              candidate.Name,
		Phone:             candidate.Phone,
		Location:          candidate.Location,
		Skills:            candidate.Skills,
		Experience:        experience,
		Education:         education,
		ExperienceYears:   int32(candidate.ExperienceYears),
		PreferredRoles:    candidate.PreferredRoles,
		SalaryExpectation: candidate.SalaryExpectation,
		Status:            candidate.Status,
		CreatedAt:         timestamppb.New(candidate.CreatedAt),
		UpdatedAt:         timestamppb.New(candidate.UpdatedAt),
	}
} 