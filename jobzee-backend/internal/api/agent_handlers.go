package api

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/jobzee/jobzee-backend/internal/services"
	"github.com/jobzee/jobzee-backend/internal/utils"
)

// AgentHandlers handles agent-related API endpoints
type AgentHandlers struct {
	agentService *services.AgentService
}

// NewAgentHandlers creates a new instance of AgentHandlers
func NewAgentHandlers(agentService *services.AgentService) *AgentHandlers {
	return &AgentHandlers{
		agentService: agentService,
	}
}

// ChatRequest represents a chat message request
type ChatRequest struct {
	UserID    string                 `json:"userId" binding:"required"`
	Message   string                 `json:"message" binding:"required"`
	AgentType string                 `json:"agentType" binding:"required"`
	Timestamp string                 `json:"timestamp"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// ChatResponse represents a chat message response
type ChatResponse struct {
	Message        string                 `json:"message"`
	Type           string                 `json:"type,omitempty"`
	Data           map[string]interface{} `json:"data,omitempty"`
	ProfileComplete bool                  `json:"profileComplete,omitempty"`
	MatchFound     bool                  `json:"matchFound,omitempty"`
	Timestamp      string                `json:"timestamp"`
	Error          string                `json:"error,omitempty"`
}

// ProcessJobRequest handles job finder agent requests
func (h *AgentHandlers) ProcessJobRequest(c *gin.Context) {
	var req ChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request format", err)
		return
	}

	// Validate agent type
	if req.AgentType != "job-finder" {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid agent type", nil)
		return
	}

	// Process the request through the agent service
	response, err := h.agentService.ProcessJobFinderRequest(req.UserID, req.Message, req.Metadata)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to process request", err)
		return
	}

	// Send response
	c.JSON(http.StatusOK, ChatResponse{
		Message:        response.Message,
		Type:           response.Type,
		Data:           response.Data,
		ProfileComplete: response.ProfileComplete,
		MatchFound:     response.MatchFound,
		Timestamp:      time.Now().UTC().Format(time.RFC3339),
	})
}

// ProcessCandidateRequest handles candidate finder agent requests
func (h *AgentHandlers) ProcessCandidateRequest(c *gin.Context) {
	var req ChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request format", err)
		return
	}

	// Validate agent type
	if req.AgentType != "candidate-finder" {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid agent type", nil)
		return
	}

	// Process the request through the agent service
	response, err := h.agentService.ProcessCandidateFinderRequest(req.UserID, req.Message, req.Metadata)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to process request", err)
		return
	}

	// Send response
	c.JSON(http.StatusOK, ChatResponse{
		Message:        response.Message,
		Type:           response.Type,
		Data:           response.Data,
		ProfileComplete: response.ProfileComplete,
		MatchFound:     response.MatchFound,
		Timestamp:      time.Now().UTC().Format(time.RFC3339),
	})
}

// GetAgentStatus returns the status of all agents
func (h *AgentHandlers) GetAgentStatus(c *gin.Context) {
	status, err := h.agentService.GetAgentStatus()
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to get agent status", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   status,
	})
}

// CreateJobPosting handles job posting creation through candidate finder agent
func (h *AgentHandlers) CreateJobPosting(c *gin.Context) {
	var req struct {
		UserID         string                 `json:"userId" binding:"required"`
		JobDescription string                 `json:"jobDescription" binding:"required"`
		Requirements   map[string]interface{} `json:"requirements"`
		Metadata       map[string]interface{} `json:"metadata,omitempty"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request format", err)
		return
	}

	// Create job posting through agent service
	jobPosting, err := h.agentService.CreateJobPosting(req.UserID, req.JobDescription, req.Requirements, req.Metadata)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to create job posting", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   jobPosting,
	})
}

// GetCandidateMatches returns matches for a job posting
func (h *AgentHandlers) GetCandidateMatches(c *gin.Context) {
	jobID := c.Param("jobId")
	if jobID == "" {
		utils.ErrorResponse(c, http.StatusBadRequest, "Job ID is required", nil)
		return
	}

	matches, err := h.agentService.GetCandidateMatches(jobID)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to get candidate matches", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   matches,
	})
}

// GetJobMatches returns job matches for a candidate
func (h *AgentHandlers) GetJobMatches(c *gin.Context) {
	candidateID := c.Param("candidateId")
	if candidateID == "" {
		utils.ErrorResponse(c, http.StatusBadRequest, "Candidate ID is required", nil)
		return
	}

	matches, err := h.agentService.GetJobMatches(candidateID)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to get job matches", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   matches,
	})
}

// ScheduleInterview handles interview scheduling
func (h *AgentHandlers) ScheduleInterview(c *gin.Context) {
	var req struct {
		CandidateID string    `json:"candidateId" binding:"required"`
		JobID       string    `json:"jobId" binding:"required"`
		InterviewDate time.Time `json:"interviewDate" binding:"required"`
		Duration    int       `json:"duration"` // in minutes
		Type        string    `json:"type"`     // phone, video, onsite
		Notes       string    `json:"notes"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request format", err)
		return
	}

	interview, err := h.agentService.ScheduleInterview(req.CandidateID, req.JobID, req.InterviewDate, req.Duration, req.Type, req.Notes)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to schedule interview", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   interview,
	})
}

// GetConversationHistory returns conversation history for a user
func (h *AgentHandlers) GetConversationHistory(c *gin.Context) {
	userID := c.Param("userId")
	if userID == "" {
		utils.ErrorResponse(c, http.StatusBadRequest, "User ID is required", nil)
		return
	}

	agentType := c.Query("agentType")
	if agentType == "" {
		utils.ErrorResponse(c, http.StatusBadRequest, "Agent type is required", nil)
		return
	}

	history, err := h.agentService.GetConversationHistory(userID, agentType)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to get conversation history", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   history,
	})
}

// UpdateCandidateProfile updates candidate profile through job finder agent
func (h *AgentHandlers) UpdateCandidateProfile(c *gin.Context) {
	var req struct {
		UserID  string                 `json:"userId" binding:"required"`
		Profile map[string]interface{} `json:"profile" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request format", err)
		return
	}

	profile, err := h.agentService.UpdateCandidateProfile(req.UserID, req.Profile)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to update candidate profile", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   profile,
	})
}

// GetAgentAnalytics returns analytics for agent performance
func (h *AgentHandlers) GetAgentAnalytics(c *gin.Context) {
	agentType := c.Query("agentType")
	timeRange := c.Query("timeRange") // daily, weekly, monthly

	analytics, err := h.agentService.GetAgentAnalytics(agentType, timeRange)
	if err != nil {
		utils.ErrorResponse(c, http.StatusInternalServerError, "Failed to get agent analytics", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   analytics,
	})
}

// HealthCheck returns agent service health status
func (h *AgentHandlers) HealthCheck(c *gin.Context) {
	health, err := h.agentService.HealthCheck()
	if err != nil {
		utils.ErrorResponse(c, http.StatusServiceUnavailable, "Agent service unhealthy", err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"data":   health,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
} 