export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string[];
  skills: string[];
  experienceLevel: string;
  salaryRange: string;
  jobType: "full-time" | "part-time" | "contract" | "internship";
  remoteFriendly: boolean;
  status: "active" | "closed" | "draft";
  createdAt: string;
  updatedAt: string;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  skills: string[];
  experience: string[];
  education: string[];
  experienceYears: number;
  preferredRoles: string[];
  salaryExpectation: string;
  resumeURL: string;
  status: "active" | "inactive" | "hired";
  createdAt: string;
  updatedAt: string;
}

export interface JobRequest {
  requestId: string;
  userId: string;
  jobDescription: string;
  skills: string[];
  location: string;
  experienceLevel: string;
}

export interface JobResponse {
  requestId: string;
  status: string;
  message: string;
  matches: JobMatch[];
}

export interface JobMatch {
  jobId: string;
  title: string;
  company: string;
  location: string;
  matchScore: number;
  description: string;
}

export interface CandidateRequest {
  requestId: string;
  jobId: string;
  jobTitle: string;
  company: string;
  requiredSkills: string[];
  location: string;
  experienceLevel: string;
}

export interface CandidateResponse {
  requestId: string;
  status: string;
  message: string;
  matches: CandidateMatch[];
}

export interface CandidateMatch {
  candidateId: string;
  name: string;
  email: string;
  matchScore: number;
  skills: string[];
  experience: string;
  location: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}
