package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/jobzee/multi-agent-backend/internal/models"
	"github.com/jobzee/multi-agent-backend/internal/services"
	pb "github.com/jobzee/multi-agent-backend/proto/proto/agent_service"
)

type Handler struct {
	jobService       *services.JobService
	candidateService *services.CandidateService
	agentService     *services.AgentService
}

func NewHandler(jobService *services.JobService, candidateService *services.CandidateService, agentService *services.AgentService) *Handler {
	return &Handler{
		jobService:       jobService,
		candidateService: candidateService,
		agentService:     agentService,
	}
}

// Job handlers
func (h *Handler) CreateJob(c *gin.Context) {
	var job models.Job
	if err := c.ShouldBindJSON(&job); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	createdJob, err := h.jobService.CreateJob(c.Request.Context(), &job)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, createdJob)
}

func (h *Handler) GetJobs(c *gin.Context) {
	jobs, err := h.jobService.GetJobs(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, jobs)
}

func (h *Handler) GetJob(c *gin.Context) {
	id := c.Param("id")
	job, err := h.jobService.GetJob(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	}

	c.JSON(http.StatusOK, job)
}

// Candidate handlers
func (h *Handler) CreateCandidate(c *gin.Context) {
	var candidate models.Candidate
	if err := c.ShouldBindJSON(&candidate); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	createdCandidate, err := h.candidateService.CreateCandidate(c.Request.Context(), &candidate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, createdCandidate)
}

func (h *Handler) GetCandidates(c *gin.Context) {
	candidates, err := h.candidateService.GetCandidates(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, candidates)
}

func (h *Handler) GetCandidate(c *gin.Context) {
	id := c.Param("id")
	candidate, err := h.candidateService.GetCandidate(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Candidate not found"})
		return
	}

	c.JSON(http.StatusOK, candidate)
}

// Agent handlers
func (h *Handler) ProcessJobRequest(c *gin.Context) {
	var req models.JobRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Convert to protobuf type
	pbReq := &pb.JobRequest{
		RequestId:       req.RequestId,
		UserId:          req.UserId,
		JobDescription:  req.JobDescription,
		Skills:          req.Skills,
		Location:        req.Location,
		ExperienceLevel: req.ExperienceLevel,
	}

	response, err := h.agentService.ProcessJobRequest(c.Request.Context(), pbReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Convert response back to model type
	modelResponse := &models.JobResponse{
		RequestId: response.RequestId,
		Status:    response.Status,
		Message:   response.Message,
		Matches:   make([]models.JobMatch, len(response.Matches)),
	}

	for i, match := range response.Matches {
		modelResponse.Matches[i] = models.JobMatch{
			JobId:       match.JobId,
			Title:       match.Title,
			Company:     match.Company,
			Location:    match.Location,
			MatchScore:  match.MatchScore,
			Description: match.Description,
		}
	}

	c.JSON(http.StatusOK, modelResponse)
}

func (h *Handler) ProcessCandidateRequest(c *gin.Context) {
	var req models.CandidateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Convert to protobuf type
	pbReq := &pb.CandidateRequest{
		RequestId:       req.RequestId,
		JobId:           req.JobId,
		JobTitle:        req.JobTitle,
		Company:         req.Company,
		RequiredSkills:  req.RequiredSkills,
		Location:        req.Location,
		ExperienceLevel: req.ExperienceLevel,
	}

	response, err := h.agentService.ProcessCandidateRequest(c.Request.Context(), pbReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Convert response back to model type
	modelResponse := &models.CandidateResponse{
		RequestId: response.RequestId,
		Status:    response.Status,
		Message:   response.Message,
		Matches:   make([]models.CandidateMatch, len(response.Matches)),
	}

	for i, match := range response.Matches {
		modelResponse.Matches[i] = models.CandidateMatch{
			CandidateId: match.CandidateId,
			Name:        match.Name,
			Email:       match.Email,
			MatchScore:  match.MatchScore,
			Skills:      match.Skills,
			Experience:  match.Experience,
			Location:    match.Location,
		}
	}

	c.JSON(http.StatusOK, modelResponse)
} 