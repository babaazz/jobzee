import { create } from "zustand";
import { persist } from "zustand/middleware";
import { jwtDecode } from "jwt-decode";

interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: "candidate" | "hr" | "admin";
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (accessToken: string, refreshToken: string, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
  refreshAccessToken: (newAccessToken: string) => void;
  refreshTokens: () => Promise<boolean>;
  checkAuthStatus: () => Promise<boolean>;
}

interface AuthStore extends AuthState, AuthActions {}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      login: (accessToken: string, refreshToken: string, user: User) => {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      updateUser: (user: User) => {
        set({ user });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      refreshAccessToken: (newAccessToken: string) => {
        set({ accessToken: newAccessToken });
      },

      refreshTokens: async (): Promise<boolean> => {
        const { refreshToken } = get();
        if (!refreshToken) {
          return false;
        }

        try {
          set({ isLoading: true });

          const response = await fetch("/api/auth/refresh", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ refreshToken }),
          });

          if (response.ok) {
            const data = await response.json();
            set({
              accessToken: data.accessToken,
              refreshToken: data.refreshToken,
              isAuthenticated: true,
              isLoading: false,
            });
            return true;
          } else {
            set({ isLoading: false });
            return false;
          }
        } catch (error) {
          console.error("Token refresh failed:", error);
          set({ isLoading: false });
          return false;
        }
      },

      checkAuthStatus: async (): Promise<boolean> => {
        const { accessToken } = get();
        if (!accessToken) {
          return false;
        }

        try {
          const response = await fetch("/api/auth/verify", {
            method: "GET",
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          });

          return response.ok;
        } catch (error) {
          console.error("Auth status check failed:", error);
          return false;
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Utility function to decode JWT token
export const decodeToken = (token: string): any => {
  try {
    return jwtDecode(token);
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
};

// Utility function to check if token is expired
export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp ? decoded.exp < currentTime : true;
  } catch (error) {
    return true;
  }
};

// Utility function to get token expiration time
export const getTokenExpiration = (token: string): Date | null => {
  try {
    const decoded = jwtDecode(token);
    return decoded.exp ? new Date(decoded.exp * 1000) : null;
  } catch (error) {
    return null;
  }
};

// Utility function to get time until token expiration in milliseconds
export const getTimeUntilExpiration = (token: string): number => {
  try {
    const decoded = jwtDecode(token);
    if (!decoded.exp) {
      return 0;
    }
    const currentTime = Date.now() / 1000;
    return Math.max((decoded.exp - currentTime) * 1000, 0);
  } catch (error) {
    return 0;
  }
};
