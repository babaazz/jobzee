# Authentication Implementation Guide

## Overview

This document describes the production-grade authentication system implemented in the JobZee frontend application. The system includes JWT token management, automatic token refresh, session persistence, and secure route protection.

## Architecture

### Components

1. **AuthStore** (`lib/auth-store.ts`) - Zustand-based state management
2. **AuthProvider** (`lib/auth-provider.tsx`) - React context for authentication
3. **AuthAPI** (`lib/auth-api.ts`) - API client for authentication endpoints
4. **API Interceptor** (`lib/api-interceptor.ts`) - Automatic token refresh and request handling
5. **ProtectedRoute** (`components/auth/ProtectedRoute.tsx`) - Route protection component
6. **Login/Register Forms** - Authentication forms with validation

### Key Features

- ✅ JWT token management with automatic refresh
- ✅ Persistent authentication state
- ✅ Automatic logout on token expiration
- ✅ Protected routes with role-based access
- ✅ Production-grade error handling
- ✅ Session management across browser tabs
- ✅ Secure token storage

## Setup

### Environment Configuration

The application uses the following environment variables:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
```

### Backend API Endpoints

The authentication system expects the following backend endpoints:

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/profile` - Get user profile
- `PUT /api/v1/profile` - Update user profile

## Usage

### 1. Authentication Provider

Wrap your app with the `AuthProvider`:

```tsx
import { AuthProvider } from "./lib/auth-provider";

export default function Layout({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
```

### 2. Protected Routes

Use the `ProtectedRoute` component to protect pages:

```tsx
import { ProtectedRoute } from "../components/auth/ProtectedRoute";

export default function DashboardPage() {
  return (
    <ProtectedRoute requiredRole="candidate">
      <DashboardContent />
    </ProtectedRoute>
  );
}
```

### 3. Authentication Hooks

Use the `useAuth` hook in your components:

```tsx
import { useAuth } from "../lib/auth-provider";

export default function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  // Your component logic
}
```

### 4. API Calls

The `AuthAPI` class handles all authentication-related API calls:

```tsx
import { authAPI } from "../lib/auth-api";

// Login
const response = await authAPI.login({
  email: "user@example.com",
  password: "password123",
});

// Register
const response = await authAPI.register({
  email: "user@example.com",
  password: "password123",
  firstName: "John",
  lastName: "Doe",
  role: "candidate",
});
```

## Token Management

### Automatic Token Refresh

The system automatically refreshes tokens:

1. **Before Expiration**: Tokens are refreshed 5 minutes before expiration
2. **On 401 Response**: If a request returns 401, the system attempts to refresh the token and retry
3. **On Page Visibility**: When the user returns to the tab, tokens are checked and refreshed if needed

### Token Storage

Tokens are stored securely using Zustand's persist middleware:

- **Access Token**: Used for API authentication
- **Refresh Token**: Used to obtain new access tokens
- **User Data**: Basic user information for UI display

### Security Features

- Tokens are automatically cleared on logout
- Expired tokens trigger automatic logout
- Failed refresh attempts result in logout
- Cross-tab session synchronization

## Error Handling

### Authentication Errors

The system handles various authentication errors:

```tsx
try {
  await authAPI.login(credentials);
} catch (error) {
  // Handle specific error types
  if (error.message.includes("Invalid credentials")) {
    // Show credential error
  } else if (error.message.includes("Account locked")) {
    // Show account locked message
  } else {
    // Show generic error
  }
}
```

### Network Errors

Network errors are handled gracefully:

- Failed requests are retried with token refresh
- Offline scenarios are handled
- Timeout errors are managed

## Testing

### API Testing

Use the provided test script to verify API connectivity:

```bash
cd jobzee-frontend
node scripts/test-api.js
```

### Manual Testing

1. **Registration Flow**:

   - Navigate to `/auth/register`
   - Fill out the form
   - Verify successful registration and redirect to dashboard

2. **Login Flow**:

   - Navigate to `/auth/login`
   - Enter credentials
   - Verify successful login and redirect to dashboard

3. **Token Refresh**:

   - Login and wait for token to expire
   - Verify automatic refresh or logout

4. **Protected Routes**:
   - Try accessing `/dashboard` without authentication
   - Verify redirect to login page

## Production Considerations

### Security

- Use HTTPS in production
- Implement rate limiting on auth endpoints
- Add CSRF protection
- Use secure cookie settings
- Implement proper CORS configuration

### Performance

- Token refresh happens in the background
- Minimal impact on user experience
- Efficient state management with Zustand

### Monitoring

- Log authentication events
- Monitor token refresh failures
- Track authentication success rates
- Alert on unusual authentication patterns

## Troubleshooting

### Common Issues

1. **API Connection Failed**:

   - Check if backend is running
   - Verify API URL configuration
   - Check network connectivity

2. **Token Refresh Fails**:

   - Check refresh token validity
   - Verify backend refresh endpoint
   - Check token expiration settings

3. **Authentication State Lost**:
   - Check localStorage permissions
   - Verify Zustand persistence
   - Check for browser storage issues

### Debug Mode

Enable debug logging by setting:

```javascript
localStorage.setItem("auth-debug", "true");
```

This will log all authentication events to the console.

## API Response Format

The backend should return responses in this format:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "candidate"
    },
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 86400
  }
}
```

## Future Enhancements

- [ ] Multi-factor authentication
- [ ] Social login integration
- [ ] Remember me functionality
- [ ] Session management dashboard
- [ ] Advanced role-based permissions
- [ ] Audit logging
- [ ] Account lockout protection
