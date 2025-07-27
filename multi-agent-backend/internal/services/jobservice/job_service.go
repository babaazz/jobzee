package jobservice

import (
	"context"
	"fmt"
	"time"

	"github.com/jobzee/multi-agent-backend/internal/database"
	"github.com/jobzee/multi-agent-backend/internal/models"
	pb "github.com/jobzee/multi-agent-backend/proto/proto/job_service"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/timestamppb"
	"gorm.io/gorm"
)

type JobService struct {
	pb.UnimplementedJobServiceServer
	db *database.Connection
}

func NewJobService(db *database.Connection) *JobService {
	return &JobService{db: db}
}

func (s *JobService) CreateJob(ctx context.Context, req *pb.CreateJobRequest) (*pb.Job, error) {
	job := &models.Job{
		Title:          req.Title,
		Company:        req.Company,
		Location:       req.Location,
		Description:    req.Description,
		Requirements:   req.Requirements,
		Skills:         req.Skills,
		ExperienceLevel: req.ExperienceLevel,
		SalaryRange:    req.SalaryRange,
		JobType:        req.JobType,
		RemoteFriendly: req.RemoteFriendly,
		Status:         "active",
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
	}

	if err := s.db.DB.WithContext(ctx).Create(job).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to create job: %v", err)
	}

	return s.jobModelToProto(job), nil
}

func (s *JobService) GetJob(ctx context.Context, req *pb.GetJobRequest) (*pb.Job, error) {
	var job models.Job
	if err := s.db.DB.WithContext(ctx).Where("id = ?", req.Id).First(&job).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, status.Errorf(codes.NotFound, "job not found")
		}
		return nil, status.Errorf(codes.Internal, "failed to get job: %v", err)
	}

	return s.jobModelToProto(&job), nil
}

func (s *JobService) ListJobs(ctx context.Context, req *pb.ListJobsRequest) (*pb.ListJobsResponse, error) {
	var jobs []models.Job
	query := s.db.DB.WithContext(ctx)

	// Apply filters
	if req.Company != "" {
		query = query.Where("company ILIKE ?", "%"+req.Company+"%")
	}
	if req.Location != "" {
		query = query.Where("location ILIKE ?", "%"+req.Location+"%")
	}
	if req.ExperienceLevel != "" {
		query = query.Where("experience_level = ?", req.ExperienceLevel)
	}
	if req.JobType != "" {
		query = query.Where("job_type = ?", req.JobType)
	}
	if req.RemoteFriendly {
		query = query.Where("remote_friendly = ?", true)
	}

	// Get total count
	var total int64
	query.Model(&models.Job{}).Count(&total)

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

	if err := query.Find(&jobs).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to list jobs: %v", err)
	}

	// Convert to proto
	protoJobs := make([]*pb.Job, len(jobs))
	for i, job := range jobs {
		protoJobs[i] = s.jobModelToProto(&job)
	}

	return &pb.ListJobsResponse{
		Jobs:        protoJobs,
		TotalCount:  int32(total),
		NextPageToken: fmt.Sprintf("%d", len(protoJobs)),
	}, nil
}

func (s *JobService) UpdateJob(ctx context.Context, req *pb.UpdateJobRequest) (*pb.Job, error) {
	var job models.Job
	if err := s.db.DB.WithContext(ctx).Where("id = ?", req.Id).First(&job).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, status.Errorf(codes.NotFound, "job not found")
		}
		return nil, status.Errorf(codes.Internal, "failed to get job: %v", err)
	}

	// Update fields
	if req.Job.Title != "" {
		job.Title = req.Job.Title
	}
	if req.Job.Company != "" {
		job.Company = req.Job.Company
	}
	if req.Job.Location != "" {
		job.Location = req.Job.Location
	}
	if req.Job.Description != "" {
		job.Description = req.Job.Description
	}
	if len(req.Job.Requirements) > 0 {
		job.Requirements = req.Job.Requirements
	}
	if len(req.Job.Skills) > 0 {
		job.Skills = req.Job.Skills
	}
	if req.Job.ExperienceLevel != "" {
		job.ExperienceLevel = req.Job.ExperienceLevel
	}
	if req.Job.SalaryRange != "" {
		job.SalaryRange = req.Job.SalaryRange
	}
	if req.Job.JobType != "" {
		job.JobType = req.Job.JobType
	}
	job.RemoteFriendly = req.Job.RemoteFriendly
	if req.Job.Status != "" {
		job.Status = req.Job.Status
	}
	job.UpdatedAt = time.Now()

	if err := s.db.DB.WithContext(ctx).Save(&job).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to update job: %v", err)
	}

	return s.jobModelToProto(&job), nil
}

func (s *JobService) DeleteJob(ctx context.Context, req *pb.DeleteJobRequest) (*emptypb.Empty, error) {
	if err := s.db.DB.WithContext(ctx).Delete(&models.Job{}, "id = ?", req.Id).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to delete job: %v", err)
	}

	return &emptypb.Empty{}, nil
}

func (s *JobService) SearchJobs(ctx context.Context, req *pb.SearchJobsRequest) (*pb.SearchJobsResponse, error) {
	var jobs []models.Job
	query := s.db.DB.WithContext(ctx)

	// Apply search criteria
	if req.Query != "" {
		query = query.Where("title ILIKE ? OR description ILIKE ?", "%"+req.Query+"%", "%"+req.Query+"%")
	}
	if len(req.Skills) > 0 {
		query = query.Where("skills && ?", req.Skills)
	}
	if req.Location != "" {
		query = query.Where("location ILIKE ?", "%"+req.Location+"%")
	}
	if req.ExperienceLevel != "" {
		query = query.Where("experience_level = ?", req.ExperienceLevel)
	}
	if req.SalaryRange != "" {
		query = query.Where("salary_range = ?", req.SalaryRange)
	}
	if req.RemoteFriendly {
		query = query.Where("remote_friendly = ?", true)
	}

	// Get total count
	var total int64
	query.Model(&models.Job{}).Count(&total)

	// Apply pagination
	limit := int(req.PageSize)
	if limit == 0 {
		limit = 10
	}
	query = query.Limit(limit)

	if req.PageToken != "" {
		query = query.Offset(limit)
	}

	if err := query.Find(&jobs).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "failed to search jobs: %v", err)
	}

	// Convert to proto
	protoJobs := make([]*pb.Job, len(jobs))
	relevanceScores := make([]float32, len(jobs))
	for i, job := range jobs {
		protoJobs[i] = s.jobModelToProto(&job)
		relevanceScores[i] = 0.8 // Placeholder score - in production, calculate based on search relevance
	}

	return &pb.SearchJobsResponse{
		Jobs:           protoJobs,
		TotalCount:     int32(total),
		NextPageToken:  fmt.Sprintf("%d", len(protoJobs)),
		RelevanceScores: relevanceScores,
	}, nil
}

func (s *JobService) GetJobStats(ctx context.Context, req *pb.GetJobStatsRequest) (*pb.JobStats, error) {
	query := s.db.DB.WithContext(ctx)

	// Apply filters
	if req.Company != "" {
		query = query.Where("company = ?", req.Company)
	}
	if req.Location != "" {
		query = query.Where("location = ?", req.Location)
	}

	// Get basic stats
	var totalJobs, activeJobs, remoteJobs int64
	query.Model(&models.Job{}).Count(&totalJobs)
	query.Where("status = ?", "active").Count(&activeJobs)
	query.Where("remote_friendly = ?", true).Count(&remoteJobs)

	// Get jobs by experience level
	var experienceStats []struct {
		ExperienceLevel string
		Count           int64
	}
	query.Model(&models.Job{}).
		Select("experience_level, count(*) as count").
		Group("experience_level").
		Scan(&experienceStats)

	experienceMap := make(map[string]int32)
	for _, stat := range experienceStats {
		experienceMap[stat.ExperienceLevel] = int32(stat.Count)
	}

	// Get jobs by location
	var locationStats []struct {
		Location string
		Count    int64
	}
	query.Model(&models.Job{}).
		Select("location, count(*) as count").
		Group("location").
		Scan(&locationStats)

	locationMap := make(map[string]int32)
	for _, stat := range locationStats {
		locationMap[stat.Location] = int32(stat.Count)
	}

	// Get jobs by company
	var companyStats []struct {
		Company string
		Count   int64
	}
	query.Model(&models.Job{}).
		Select("company, count(*) as count").
		Group("company").
		Scan(&companyStats)

	companyMap := make(map[string]int32)
	for _, stat := range companyStats {
		companyMap[stat.Company] = int32(stat.Count)
	}

	return &pb.JobStats{
		TotalJobs:              int32(totalJobs),
		ActiveJobs:             int32(activeJobs),
		RemoteJobs:             int32(remoteJobs),
		JobsByExperienceLevel:  experienceMap,
		JobsByLocation:         locationMap,
		JobsByCompany:          companyMap,
		TopSkills:              []string{}, // TODO: Implement top skills calculation
		LastUpdated:            timestamppb.Now(),
	}, nil
}

// Helper function to convert model to proto
func (s *JobService) jobModelToProto(job *models.Job) *pb.Job {
	return &pb.Job{
		Id:              job.ID,
		Title:           job.Title,
		Company:         job.Company,
		Location:        job.Location,
		Description:     job.Description,
		Requirements:    job.Requirements,
		Skills:          job.Skills,
		ExperienceLevel: job.ExperienceLevel,
		SalaryRange:     job.SalaryRange,
		JobType:         job.JobType,
		RemoteFriendly:  job.RemoteFriendly,
		Status:          job.Status,
		CreatedAt:       timestamppb.New(job.CreatedAt),
		UpdatedAt:       timestamppb.New(job.UpdatedAt),
	}
} 