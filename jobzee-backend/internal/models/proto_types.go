package models

// Placeholder proto types until we generate from .proto files
type JobRequest struct {
	RequestId       string   `json:"request_id"`
	UserId          string   `json:"user_id"`
	JobDescription  string   `json:"job_description"`
	Skills          []string `json:"skills"`
	Location        string   `json:"location"`
	ExperienceLevel string   `json:"experience_level"`
}

type JobResponse struct {
	RequestId string      `json:"request_id"`
	Status    string      `json:"status"`
	Message   string      `json:"message"`
	Matches   []JobMatch  `json:"matches"`
}

type JobMatch struct {
	JobId       string  `json:"job_id"`
	Title       string  `json:"title"`
	Company     string  `json:"company"`
	Location    string  `json:"location"`
	MatchScore  float64 `json:"match_score"`
	Description string  `json:"description"`
}

type CandidateRequest struct {
	RequestId      string   `json:"request_id"`
	JobId          string   `json:"job_id"`
	JobTitle       string   `json:"job_title"`
	Company        string   `json:"company"`
	RequiredSkills []string `json:"required_skills"`
	Location       string   `json:"location"`
	ExperienceLevel string  `json:"experience_level"`
}

type CandidateResponse struct {
	RequestId string            `json:"request_id"`
	Status    string            `json:"status"`
	Message   string            `json:"message"`
	Matches   []CandidateMatch  `json:"matches"`
}

type CandidateMatch struct {
	CandidateId string   `json:"candidate_id"`
	Name        string   `json:"name"`
	Email       string   `json:"email"`
	MatchScore  float64  `json:"match_score"`
	Skills      []string `json:"skills"`
	Experience  string   `json:"experience"`
	Location    string   `json:"location"`
} 