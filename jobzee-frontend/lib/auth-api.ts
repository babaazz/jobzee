import { useAuthStore } from "./auth-store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: "candidate" | "hr";
  phone?: string;
  location?: string;
  companyId?: number;
}

interface AuthResponse {
  user: {
    id: number;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
  };
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

class AuthAPI {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}/api/v1${endpoint}`;

    const defaultHeaders: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // Add authorization header if token exists
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      defaultHeaders["Authorization"] = `Bearer ${accessToken}`;
    }

    const config: RequestInit = {
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || `HTTP error! status: ${response.status}`
        );
      }

      return data;
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });

    if (!response.success || !response.data) {
      throw new Error(response.message || "Login failed");
    }

    return response.data;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });

    if (!response.success || !response.data) {
      throw new Error(response.message || "Registration failed");
    }

    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.success || !response.data) {
      throw new Error(response.message || "Token refresh failed");
    }

    return response.data;
  }

  async getProfile(): Promise<any> {
    const response = await this.request<any>("/profile", {
      method: "GET",
    });

    if (!response.success || !response.data) {
      throw new Error(response.message || "Failed to get profile");
    }

    return response.data;
  }

  async updateProfile(profileData: Partial<any>): Promise<any> {
    const response = await this.request<any>("/profile", {
      method: "PUT",
      body: JSON.stringify(profileData),
    });

    if (!response.success || !response.data) {
      throw new Error(response.message || "Failed to update profile");
    }

    return response.data;
  }

  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<void> {
    const response = await this.request<void>("/profile/change-password", {
      method: "POST",
      body: JSON.stringify({
        currentPassword,
        newPassword,
      }),
    });

    if (!response.success) {
      throw new Error(response.message || "Failed to change password");
    }
  }

  async forgotPassword(email: string): Promise<void> {
    const response = await this.request<void>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });

    if (!response.success) {
      throw new Error(response.message || "Failed to send reset email");
    }
  }

  async resetPassword(token: string, newPassword: string): Promise<void> {
    const response = await this.request<void>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({
        token,
        newPassword,
      }),
    });

    if (!response.success) {
      throw new Error(response.message || "Failed to reset password");
    }
  }

  async logout(): Promise<void> {
    try {
      await this.request<void>("/profile/logout", {
        method: "POST",
      });
    } catch (error) {
      // Don't throw error for logout, just log it
      console.warn("Logout request failed:", error);
    }
  }
}

export const authAPI = new AuthAPI();
