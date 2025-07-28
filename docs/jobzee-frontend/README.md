# JobZee Frontend Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Component Architecture](#component-architecture)
6. [State Management](#state-management)
7. [API Integration](#api-integration)
8. [Real-time Communication](#real-time-communication)
9. [Internationalization](#internationalization)
10. [Styling & UI](#styling--ui)
11. [Testing Strategy](#testing-strategy)
12. [Performance Optimization](#performance-optimization)
13. [Deployment](#deployment)

## Overview

The JobZee Frontend is a modern, responsive web application built with Next.js 14, TypeScript, and Tailwind CSS. It provides an intuitive interface for candidates and HR professionals to interact with AI agents for job matching and recruitment.

### Key Features

- **Modern React**: Next.js 14 with App Router
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Chat**: WebSocket integration with AI agents
- **Internationalization**: Multi-language support
- **Progressive Web App**: PWA capabilities
- **Accessibility**: WCAG 2.1 compliant

## Architecture

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   Pages         │    │   Components    │    │   Hooks       │ │
│  │                 │    │                 │    │               │ │
│  │ • App Router    │    │ • UI Library    │    │ • useApi      │ │
│  │ • SSR/SSG       │    │ • Forms         │    │ • useAuth     │ │
│  │ • Dynamic       │    │ • Charts        │    │ • useWebSocket│ │
│  │ • Layouts       │    │ • Modals        │    │ • useForm     │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   State         │    │   Services      │    │   Utils       │ │
│  │   Management    │    │                 │    │               │ │
│  │                 │    │ • API Client    │    │ • Validation  │ │
│  │ • Context       │    │ • Auth Service  │    │ • Formatting  │ │
│  │ • Reducers      │    │ • WebSocket     │    │ • Constants   │ │
│  │ • Persistence   │    │ • Storage       │    │ • Helpers     │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Action   │───►│   Component     │───►│   Hook/Service  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   State Update  │◄───│   Context       │◄───│   API Call      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Re-render  │◄───│   Component     │◄───│   Response      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Core Technologies

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS 3.0+
- **State Management**: React Context + Hooks
- **HTTP Client**: Axios
- **WebSocket**: Native WebSocket API
- **Forms**: React Hook Form + Zod validation

### Development Tools

- **Package Manager**: npm
- **Linting**: ESLint + Prettier
- **Type Checking**: TypeScript
- **Testing**: Jest + React Testing Library
- **Build Tool**: Next.js built-in bundler

### UI Libraries

- **Icons**: Lucide React
- **Charts**: Recharts
- **Date Handling**: date-fns
- **Internationalization**: i18next

## Project Structure

```
jobzee-frontend/
├── app/                    # Next.js App Router
│   ├── [locale]/          # Internationalized routes
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx       # Home page
│   │   ├── auth/          # Authentication pages
│   │   ├── dashboard/     # Dashboard pages
│   │   ├── jobs/          # Job-related pages
│   │   └── profile/       # Profile pages
│   ├── globals.css        # Global styles
│   └── i18n.ts           # i18n configuration
├── components/            # Reusable components
│   ├── ui/               # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── ...
│   ├── forms/            # Form components
│   ├── layout/           # Layout components
│   ├── AgentChat.tsx     # Agent chat component
│   └── ...
├── hooks/                # Custom React hooks
│   ├── useApi.ts
│   ├── useAuth.ts
│   ├── useWebSocket.ts
│   └── ...
├── lib/                  # Utility libraries
│   ├── api.ts           # API client
│   ├── auth-api.ts      # Authentication API
│   ├── auth-store.ts    # Auth state management
│   └── ...
├── types/               # TypeScript type definitions
│   └── index.ts
├── locales/             # Translation files
│   ├── en.json
│   ├── hi.json
│   └── ...
├── styles/              # Additional styles
│   └── globals.css
├── public/              # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Component Architecture

### Component Hierarchy

```
App
├── RootLayout
│   ├── Header
│   │   ├── Logo
│   │   ├── Navigation
│   │   └── UserMenu
│   ├── Sidebar (Dashboard)
│   │   ├── NavMenu
│   │   └── QuickActions
│   ├── Main Content
│   │   ├── Page Components
│   │   └── Modals
│   └── Footer
└── Providers
    ├── AuthProvider
    ├── ThemeProvider
    └── WebSocketProvider
```

### Component Categories

#### UI Components (Base)

```typescript
// components/ui/Button.tsx
interface ButtonProps {
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  children,
  onClick,
  ...props
}) => {
  const baseClasses =
    "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background";

  const variantClasses = {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    outline: "border border-input hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
  };

  const sizeClasses = {
    sm: "h-9 px-3",
    md: "h-10 py-2 px-4",
    lg: "h-11 px-8",
  };

  return (
    <button
      className={cn(baseClasses, variantClasses[variant], sizeClasses[size])}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </button>
  );
};
```

#### Form Components

```typescript
// components/forms/JobSearchForm.tsx
interface JobSearchFormProps {
  onSearch: (filters: JobFilters) => void;
  initialFilters?: JobFilters;
}

export const JobSearchForm: React.FC<JobSearchFormProps> = ({
  onSearch,
  initialFilters = {},
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<JobFilters>({
    defaultValues: initialFilters,
  });

  const onSubmit = (data: JobFilters) => {
    onSearch(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          {...register("title")}
          placeholder="Job title"
          error={errors.title?.message}
        />
        <Input
          {...register("location")}
          placeholder="Location"
          error={errors.location?.message}
        />
        <Select {...register("jobType")}>
          <option value="">All types</option>
          <option value="full-time">Full-time</option>
          <option value="part-time">Part-time</option>
          <option value="contract">Contract</option>
        </Select>
      </div>
      <Button type="submit" className="w-full">
        Search Jobs
      </Button>
    </form>
  );
};
```

#### Layout Components

```typescript
// components/layout/DashboardLayout.tsx
interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  actions?: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  title,
  actions,
}) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {(title || actions) && (
              <div className="mb-6 flex items-center justify-between">
                {title && <h1 className="text-2xl font-bold">{title}</h1>}
                {actions && <div className="flex gap-2">{actions}</div>}
              </div>
            )}
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
```

## State Management

### Context-Based State Management

#### Authentication Context

```typescript
// lib/auth-store.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: "AUTH_START" });
    try {
      const response = await authAPI.login(credentials);
      dispatch({ type: "AUTH_SUCCESS", payload: response.user });
      localStorage.setItem("accessToken", response.accessToken);
      localStorage.setItem("refreshToken", response.refreshToken);
    } catch (error) {
      dispatch({ type: "AUTH_ERROR", payload: error.message });
    }
  };

  const logout = () => {
    dispatch({ type: "AUTH_LOGOUT" });
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  };

  const value = {
    ...state,
    login,
    logout,
    register,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

#### WebSocket Context

```typescript
// hooks/useWebSocket.ts
interface WebSocketContextType {
  socket: WebSocket | null;
  isConnected: boolean;
  sendMessage: (message: string) => void;
  connect: (agentType: string) => void;
  disconnect: () => void;
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { user } = useAuth();

  const connect = useCallback(
    (agentType: string) => {
      if (!user) return;

      const ws = new WebSocket(
        `${process.env.NEXT_PUBLIC_WS_URL}/agents/${agentType}`
      );

      ws.onopen = () => {
        setIsConnected(true);
        ws.send(
          JSON.stringify({
            type: "auth",
            token: localStorage.getItem("accessToken"),
          })
        );
      };

      ws.onclose = () => {
        setIsConnected(false);
      };

      setSocket(ws);
    },
    [user]
  );

  const disconnect = useCallback(() => {
    if (socket) {
      socket.close();
      setSocket(null);
      setIsConnected(false);
    }
  }, [socket]);

  const sendMessage = useCallback(
    (message: string) => {
      if (socket && isConnected) {
        socket.send(
          JSON.stringify({
            type: "message",
            content: message,
          })
        );
      }
    },
    [socket, isConnected]
  );

  return (
    <WebSocketContext.Provider
      value={{
        socket,
        isConnected,
        sendMessage,
        connect,
        disconnect,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
```

## API Integration

### API Client Configuration

```typescript
// lib/api.ts
class ApiClient {
  private baseURL: string;
  private axiosInstance: AxiosInstance;

  constructor() {
    this.baseURL =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1";

    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("accessToken");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          try {
            const refreshToken = localStorage.getItem("refreshToken");
            const response = await this.refreshToken(refreshToken);
            localStorage.setItem("accessToken", response.accessToken);

            // Retry original request
            error.config.headers.Authorization = `Bearer ${response.accessToken}`;
            return this.axiosInstance.request(error.config);
          } catch (refreshError) {
            // Redirect to login
            window.location.href = "/auth/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Job API methods
  async getJobs(filters?: JobFilters): Promise<Job[]> {
    const response = await this.axiosInstance.get("/jobs", { params: filters });
    return response.data.data;
  }

  async getJob(id: string): Promise<Job> {
    const response = await this.axiosInstance.get(`/jobs/${id}`);
    return response.data.data;
  }

  async createJob(jobData: CreateJobRequest): Promise<Job> {
    const response = await this.axiosInstance.post("/jobs", jobData);
    return response.data.data;
  }

  // Candidate API methods
  async getCandidates(filters?: CandidateFilters): Promise<Candidate[]> {
    const response = await this.axiosInstance.get("/candidates", {
      params: filters,
    });
    return response.data.data;
  }

  async updateProfile(profileData: ProfileUpdate): Promise<Candidate> {
    const response = await this.axiosInstance.put(
      "/candidates/profile",
      profileData
    );
    return response.data.data;
  }

  // Agent API methods
  async chatWithAgent(
    agentType: string,
    message: string
  ): Promise<AgentResponse> {
    const response = await this.axiosInstance.post(
      `/agents/${agentType}/chat`,
      {
        message,
      }
    );
    return response.data.data;
  }
}

export const apiClient = new ApiClient();
```

### Custom Hooks for API

```typescript
// hooks/useApi.ts
export const useApi = <T, E = any>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<E | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError(err as E);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    execute();
  }, [execute]);

  return { data, loading, error, refetch: execute };
};

// Usage example
export const useJobs = (filters?: JobFilters) => {
  return useApi(() => apiClient.getJobs(filters), [filters]);
};
```

## Real-time Communication

### WebSocket Integration

```typescript
// components/AgentChat.tsx
interface AgentChatProps {
  agentType: "job-finder" | "candidate-finder";
  initialMessage?: string;
}

export const AgentChat: React.FC<AgentChatProps> = ({
  agentType,
  initialMessage,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { socket, isConnected, sendMessage, connect } = useWebSocket();

  useEffect(() => {
    if (agentType) {
      connect(agentType);
    }
  }, [agentType, connect]);

  useEffect(() => {
    if (socket) {
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleIncomingMessage(data);
      };
    }
  }, [socket]);

  const handleIncomingMessage = (data: any) => {
    if (data.type === "message") {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          content: data.content,
          sender: "agent",
          timestamp: new Date(),
        },
      ]);
      setIsTyping(false);
    } else if (data.type === "typing") {
      setIsTyping(true);
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || !isConnected) return;

    const message: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, message]);
    sendMessage(inputValue);
    setInputValue("");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Type your message..."
            disabled={!isConnected}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!isConnected || !inputValue.trim()}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
```

## Internationalization

### i18n Configuration

```typescript
// app/i18n.ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  en: {
    translation: {
      common: {
        loading: "Loading...",
        error: "An error occurred",
        save: "Save",
        cancel: "Cancel",
        delete: "Delete",
        edit: "Edit",
        search: "Search",
      },
      auth: {
        login: "Login",
        register: "Register",
        logout: "Logout",
        email: "Email",
        password: "Password",
        forgotPassword: "Forgot Password?",
      },
      jobs: {
        title: "Jobs",
        searchJobs: "Search Jobs",
        jobTitle: "Job Title",
        company: "Company",
        location: "Location",
        apply: "Apply",
        applied: "Applied",
      },
      // ... more translations
    },
  },
  hi: {
    translation: {
      common: {
        loading: "लोड हो रहा है...",
        error: "एक त्रुटि हुई",
        save: "सहेजें",
        cancel: "रद्द करें",
        delete: "हटाएं",
        edit: "संपादित करें",
        search: "खोजें",
      },
      // ... Hindi translations
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
```

### Usage in Components

```typescript
// components/JobCard.tsx
import { useTranslation } from "react-i18next";

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const { t } = useTranslation();

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <h3 className="text-lg font-semibold">{job.title}</h3>
      <p className="text-gray-600">{job.company}</p>
      <p className="text-gray-500">{job.location}</p>
      <div className="mt-4 flex justify-between items-center">
        <span className="text-sm text-gray-500">
          {t("jobs.posted")}: {formatDate(job.createdAt)}
        </span>
        <Button variant="primary">{t("jobs.apply")}</Button>
      </div>
    </div>
  );
};
```

## Styling & UI

### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        secondary: {
          50: "#f8fafc",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};
```

### Component Styling Patterns

```typescript
// Utility function for conditional classes
export const cn = (...classes: (string | undefined | null | false)[]) => {
  return classes.filter(Boolean).join(" ");
};

// Responsive design patterns
const responsiveClasses = {
  container: "w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
  grid: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
  card: "bg-white rounded-lg shadow-sm border border-gray-200 p-6",
};

// Dark mode support
const darkModeClasses = {
  card: "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700",
  text: "text-gray-900 dark:text-gray-100",
  textSecondary: "text-gray-600 dark:text-gray-400",
};
```

## Testing Strategy

### Unit Testing

```typescript
// __tests__/components/Button.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "@/components/ui/Button";

describe("Button", () => {
  it("renders with correct text", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText("Click me"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByText("Click me")).toBeDisabled();
  });

  it("shows loading state", () => {
    render(<Button loading>Click me</Button>);
    expect(screen.getByTestId("spinner")).toBeInTheDocument();
  });
});
```

### Integration Testing

```typescript
// __tests__/pages/jobs.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import { JobsPage } from "@/app/[locale]/jobs/page";
import { apiClient } from "@/lib/api";

jest.mock("@/lib/api");

describe("JobsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("loads and displays jobs", async () => {
    const mockJobs = [
      { id: "1", title: "Software Engineer", company: "Tech Corp" },
      { id: "2", title: "Product Manager", company: "Startup Inc" },
    ];

    (apiClient.getJobs as jest.Mock).mockResolvedValue(mockJobs);

    render(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("Software Engineer")).toBeInTheDocument();
      expect(screen.getByText("Product Manager")).toBeInTheDocument();
    });
  });

  it("handles search functionality", async () => {
    render(<JobsPage />);

    const searchInput = screen.getByPlaceholderText("Search jobs...");
    fireEvent.change(searchInput, { target: { value: "engineer" } });

    await waitFor(() => {
      expect(apiClient.getJobs).toHaveBeenCalledWith(
        expect.objectContaining({ title: "engineer" })
      );
    });
  });
});
```

### E2E Testing

```typescript
// e2e/job-application.spec.ts
import { test, expect } from "@playwright/test";

test("user can apply for a job", async ({ page }) => {
  // Navigate to jobs page
  await page.goto("/jobs");

  // Search for a job
  await page.fill('[data-testid="job-search"]', "Software Engineer");
  await page.click('[data-testid="search-button"]');

  // Click on first job
  await page.click('[data-testid="job-card"]:first-child');

  // Click apply button
  await page.click('[data-testid="apply-button"]');

  // Fill application form
  await page.fill(
    '[data-testid="cover-letter"]',
    "I am interested in this position..."
  );
  await page.click('[data-testid="submit-application"]');

  // Verify success message
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
});
```

## Performance Optimization

### Code Splitting

```typescript
// Dynamic imports for code splitting
const AgentChat = dynamic(() => import("@/components/AgentChat"), {
  loading: () => <div>Loading chat...</div>,
  ssr: false,
});

const JobChart = dynamic(() => import("@/components/JobChart"), {
  loading: () => <div>Loading chart...</div>,
});
```

### Image Optimization

```typescript
// Next.js Image component for optimization
import Image from "next/image";

export const CompanyLogo: React.FC<{ src: string; alt: string }> = ({
  src,
  alt,
}) => {
  return (
    <Image
      src={src}
      alt={alt}
      width={100}
      height={50}
      className="object-contain"
      priority={false}
    />
  );
};
```

### Memoization

```typescript
// React.memo for component memoization
export const JobCard = React.memo<JobCardProps>(({ job, onApply }) => {
  return (
    <div className="job-card">
      <h3>{job.title}</h3>
      <p>{job.company}</p>
      <Button onClick={() => onApply(job.id)}>Apply</Button>
    </div>
  );
});

// useMemo for expensive calculations
const filteredJobs = useMemo(() => {
  return jobs.filter((job) =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [jobs, searchTerm]);

// useCallback for function memoization
const handleApply = useCallback(
  (jobId: string) => {
    applyForJob(jobId);
  },
  [applyForJob]
);
```

## Deployment

### Build Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ["localhost", "your-domain.com"],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8080/ws
NEXT_PUBLIC_APP_NAME=JobZee
NEXT_PUBLIC_APP_VERSION=1.0.0

# Production
NEXT_PUBLIC_API_URL=https://api.jobzee.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.jobzee.com/ws
```

---

## Conclusion

The JobZee Frontend is a modern, performant web application that provides:

- **Excellent User Experience**: Intuitive interface with real-time interactions
- **Scalable Architecture**: Component-based design with clear separation of concerns
- **Type Safety**: Full TypeScript implementation for better development experience
- **Performance**: Optimized with code splitting, memoization, and image optimization
- **Accessibility**: WCAG 2.1 compliant with proper semantic markup
- **Internationalization**: Multi-language support for global users
- **Testing**: Comprehensive testing strategy with unit, integration, and E2E tests

The frontend serves as the primary interface for users to interact with the JobZee platform, providing seamless access to AI-powered job matching and recruitment features.
