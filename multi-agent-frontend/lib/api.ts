import {
  Job,
  Candidate,
  JobRequest,
  JobResponse,
  CandidateRequest,
  CandidateResponse,
  ApiResponse,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  // Job endpoints
  async getJobs(): Promise<Job[]> {
    const response = await this.request<Job[]>("/jobs");
    return response.data || [];
  }

  async getJob(id: string): Promise<Job> {
    const response = await this.request<Job>(`/jobs/${id}`);
    return response.data!;
  }

  async createJob(
    job: Omit<Job, "id" | "createdAt" | "updatedAt">
  ): Promise<Job> {
    const response = await this.request<Job>("/jobs", {
      method: "POST",
      body: JSON.stringify(job),
    });
    return response.data!;
  }

  // Candidate endpoints
  async getCandidates(): Promise<Candidate[]> {
    const response = await this.request<Candidate[]>("/candidates");
    return response.data || [];
  }

  async getCandidate(id: string): Promise<Candidate> {
    const response = await this.request<Candidate>(`/candidates/${id}`);
    return response.data!;
  }

  async createCandidate(
    candidate: Omit<Candidate, "id" | "createdAt" | "updatedAt">
  ): Promise<Candidate> {
    const response = await this.request<Candidate>("/candidates", {
      method: "POST",
      body: JSON.stringify(candidate),
    });
    return response.data!;
  }

  // Agent endpoints
  async processJobRequest(request: JobRequest): Promise<JobResponse> {
    const response = await this.request<JobResponse>("/agents/job-request", {
      method: "POST",
      body: JSON.stringify(request),
    });
    return response.data!;
  }

  async processCandidateRequest(
    request: CandidateRequest
  ): Promise<CandidateResponse> {
    const response = await this.request<CandidateResponse>(
      "/agents/candidate-request",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
    return response.data!;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(
      `${this.baseUrl.replace("/api/v1", "")}/health`
    );
    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
