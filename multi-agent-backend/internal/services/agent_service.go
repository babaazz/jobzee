package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/jobzee/multi-agent-backend/internal/config"
)

// AgentService handles communication with AI agents
type AgentService struct {
	config *config.Config
	client *http.Client
}

// AgentResponse represents a response from an agent
type AgentResponse struct {
	Message        string                 `json:"message"`
	Type           string                 `json:"type,omitempty"`
	Data           map[string]interface{} `json:"data,omitempty"`
	ProfileComplete bool                  `json:"profileComplete,omitempty"`
	MatchFound     bool                  `json:"matchFound,omitempty"`
	Error          string                 `json:"error,omitempty"`
}

// AgentStatus represents the status of an agent
type AgentStatus struct {
	AgentID   string    `json:"agentId"`
	Status    string    `json:"status"`
	LastSeen  time.Time `json:"lastSeen"`
	MessageCount int    `json:"messageCount"`
	Error     string    `json:"error,omitempty"`
}

// NewAgentService creates a new agent service
func NewAgentService(cfg *config.Config) *AgentService {
	return &AgentService{
		config: cfg,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// ProcessJobFinderRequest processes a request through the job finder agent
func (s *AgentService) ProcessJobFinderRequest(userID, message string, metadata map[string]interface{}) (*AgentResponse, error) {
	request := map[string]interface{}{
		"userId":   userID,
		"message":  message,
		"metadata": metadata,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}

	response, err := s.sendAgentRequest("job-finder", request)
	if err != nil {
		return nil, fmt.Errorf("failed to process job finder request: %w", err)
	}

	return response, nil
}

// ProcessCandidateFinderRequest processes a request through the candidate finder agent
func (s *AgentService) ProcessCandidateFinderRequest(userID, message string, metadata map[string]interface{}) (*AgentResponse, error) {
	request := map[string]interface{}{
		"userId":   userID,
		"message":  message,
		"metadata": metadata,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}

	response, err := s.sendAgentRequest("candidate-finder", request)
	if err != nil {
		return nil, fmt.Errorf("failed to process candidate finder request: %w", err)
	}

	return response, nil
}

// sendAgentRequest sends a request to a specific agent
func (s *AgentService) sendAgentRequest(agentType string, request map[string]interface{}) (*AgentResponse, error) {
	// Determine agent endpoint based on type
	var endpoint string
	switch agentType {
	case "job-finder":
		endpoint = fmt.Sprintf("http://localhost:8084/chat")
	case "candidate-finder":
		endpoint = fmt.Sprintf("http://localhost:8085/chat")
	default:
		return nil, fmt.Errorf("unknown agent type: %s", agentType)
	}

	// Marshal request to JSON
	requestBody, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Send HTTP request
	resp, err := s.client.Post(endpoint, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("failed to send request to agent: %w", err)
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("agent returned status %d", resp.StatusCode)
	}

	// Decode response
	var agentResponse AgentResponse
	if err := json.NewDecoder(resp.Body).Decode(&agentResponse); err != nil {
		return nil, fmt.Errorf("failed to decode agent response: %w", err)
	}

	return &agentResponse, nil
}

// GetAgentStatus returns the status of all agents
func (s *AgentService) GetAgentStatus() (map[string]AgentStatus, error) {
	agents := map[string]string{
		"job-finder":      "http://localhost:8084/health",
		"candidate-finder": "http://localhost:8085/health",
	}

	status := make(map[string]AgentStatus)

	for agentID, endpoint := range agents {
		agentStatus, err := s.getAgentHealth(endpoint)
		if err != nil {
			status[agentID] = AgentStatus{
				AgentID:  agentID,
				Status:   "unhealthy",
				LastSeen: time.Now(),
				Error:    err.Error(),
			}
		} else {
			status[agentID] = *agentStatus
		}
	}

	return status, nil
}

// getAgentHealth checks the health of a specific agent
func (s *AgentService) getAgentHealth(endpoint string) (*AgentStatus, error) {
	resp, err := s.client.Get(endpoint)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("agent returned status %d", resp.StatusCode)
	}

	var healthResponse struct {
		Status       string    `json:"status"`
		LastSeen     time.Time `json:"lastSeen"`
		MessageCount int       `json:"messageCount"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&healthResponse); err != nil {
		return nil, err
	}

	return &AgentStatus{
		Status:       healthResponse.Status,
		LastSeen:     healthResponse.LastSeen,
		MessageCount: healthResponse.MessageCount,
	}, nil
}

// CreateJobPosting creates a job posting through the candidate finder agent
func (s *AgentService) CreateJobPosting(userID, jobDescription string, requirements, metadata map[string]interface{}) (map[string]interface{}, error) {
	request := map[string]interface{}{
		"userId":         userID,
		"jobDescription": jobDescription,
		"requirements":   requirements,
		"metadata":       metadata,
		"action":         "create_job_posting",
	}

	response, err := s.sendAgentRequest("candidate-finder", request)
	if err != nil {
		return nil, err
	}

	return response.Data, nil
}

// GetCandidateMatches returns candidate matches for a job
func (s *AgentService) GetCandidateMatches(jobID string) ([]map[string]interface{}, error) {
	request := map[string]interface{}{
		"jobId":  jobID,
		"action": "get_candidate_matches",
	}

	response, err := s.sendAgentRequest("candidate-finder", request)
	if err != nil {
		return nil, err
	}

	// Extract matches from response data
	if matches, ok := response.Data["matches"]; ok {
		if matchList, ok := matches.([]map[string]interface{}); ok {
			return matchList, nil
		}
	}

	return []map[string]interface{}{}, nil
}

// GetJobMatches returns job matches for a candidate
func (s *AgentService) GetJobMatches(candidateID string) ([]map[string]interface{}, error) {
	request := map[string]interface{}{
		"candidateId": candidateID,
		"action":      "get_job_matches",
	}

	response, err := s.sendAgentRequest("job-finder", request)
	if err != nil {
		return nil, err
	}

	// Extract matches from response data
	if matches, ok := response.Data["matches"]; ok {
		if matchList, ok := matches.([]map[string]interface{}); ok {
			return matchList, nil
		}
	}

	return []map[string]interface{}{}, nil
}

// ScheduleInterview schedules an interview between a candidate and employer
func (s *AgentService) ScheduleInterview(candidateID, jobID string, interviewDate time.Time, duration int, interviewType, notes string) (map[string]interface{}, error) {
	request := map[string]interface{}{
		"candidateId":   candidateID,
		"jobId":         jobID,
		"interviewDate": interviewDate.Format(time.RFC3339),
		"duration":      duration,
		"type":          interviewType,
		"notes":         notes,
		"action":        "schedule_interview",
	}

	response, err := s.sendAgentRequest("candidate-finder", request)
	if err != nil {
		return nil, err
	}

	return response.Data, nil
}

// GetConversationHistory returns conversation history for a user
func (s *AgentService) GetConversationHistory(userID, agentType string) ([]map[string]interface{}, error) {
	request := map[string]interface{}{
		"userId":    userID,
		"agentType": agentType,
		"action":    "get_conversation_history",
	}

	response, err := s.sendAgentRequest(agentType, request)
	if err != nil {
		return nil, err
	}

	// Extract history from response data
	if history, ok := response.Data["history"]; ok {
		if historyList, ok := history.([]map[string]interface{}); ok {
			return historyList, nil
		}
	}

	return []map[string]interface{}{}, nil
}

// UpdateCandidateProfile updates a candidate's profile
func (s *AgentService) UpdateCandidateProfile(userID string, profile map[string]interface{}) (map[string]interface{}, error) {
	request := map[string]interface{}{
		"userId":  userID,
		"profile": profile,
		"action":  "update_profile",
	}

	response, err := s.sendAgentRequest("job-finder", request)
	if err != nil {
		return nil, err
	}

	return response.Data, nil
}

// GetAgentAnalytics returns analytics for agent performance
func (s *AgentService) GetAgentAnalytics(agentType, timeRange string) (map[string]interface{}, error) {
	request := map[string]interface{}{
		"agentType": agentType,
		"timeRange": timeRange,
		"action":    "get_analytics",
	}

	response, err := s.sendAgentRequest(agentType, request)
	if err != nil {
		return nil, err
	}

	return response.Data, nil
}

// HealthCheck performs a health check on the agent service
func (s *AgentService) HealthCheck() (map[string]interface{}, error) {
	status, err := s.GetAgentStatus()
	if err != nil {
		return map[string]interface{}{
			"status": "unhealthy",
			"error":  err.Error(),
		}, err
	}

	// Check if all agents are healthy
	allHealthy := true
	for _, agentStatus := range status {
		if agentStatus.Status != "healthy" {
			allHealthy = false
			break
		}
	}

	health := map[string]interface{}{
		"status":  "healthy",
		"agents":  status,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}

	if !allHealthy {
		health["status"] = "degraded"
	}

	return health, nil
} 