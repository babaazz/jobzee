package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/jobzee/multi-agent-backend/internal/models"
	"github.com/jobzee/multi-agent-backend/internal/services"
	"github.com/jobzee/multi-agent-backend/internal/utils"
)

type AuthHandler struct {
	authService *services.AuthService
}

func NewAuthHandler(authService *services.AuthService) *AuthHandler {
	return &AuthHandler{
		authService: authService,
	}
}

// Register handles user registration
func (h *AuthHandler) Register(c *gin.Context) {
	var req models.RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	response, err := h.authService.Register(&req)
	if err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Registration failed", err)
		return
	}

	utils.SuccessResponse(c, http.StatusCreated, "User registered successfully", response)
}

// Login handles user login
func (h *AuthHandler) Login(c *gin.Context) {
	var req models.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	response, err := h.authService.Login(&req)
	if err != nil {
		utils.ErrorResponse(c, http.StatusUnauthorized, "Login failed", err)
		return
	}

	utils.SuccessResponse(c, http.StatusOK, "Login successful", response)
}

// RefreshToken handles token refresh
func (h *AuthHandler) RefreshToken(c *gin.Context) {
	var req models.RefreshTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	response, err := h.authService.RefreshToken(req.RefreshToken)
	if err != nil {
		utils.ErrorResponse(c, http.StatusUnauthorized, "Token refresh failed", err)
		return
	}

	utils.SuccessResponse(c, http.StatusOK, "Token refreshed successfully", response)
}

// ChangePassword handles password change
func (h *AuthHandler) ChangePassword(c *gin.Context) {
	userID, exists := utils.GetCurrentUserID(c)
	if !exists {
		utils.ErrorResponse(c, http.StatusUnauthorized, "User not authenticated", nil)
		return
	}

	var req models.ChangePasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	err := h.authService.ChangePassword(userID, &req)
	if err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Password change failed", err)
		return
	}

	utils.SuccessResponse(c, http.StatusOK, "Password changed successfully", nil)
}

// UpdateProfile handles profile updates
func (h *AuthHandler) UpdateProfile(c *gin.Context) {
	userID, exists := utils.GetCurrentUserID(c)
	if !exists {
		utils.ErrorResponse(c, http.StatusUnauthorized, "User not authenticated", nil)
		return
	}

	var req models.UpdateProfileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	user, err := h.authService.UpdateProfile(userID, &req)
	if err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Profile update failed", err)
		return
	}

	utils.SuccessResponse(c, http.StatusOK, "Profile updated successfully", user)
}

// GetProfile gets the current user's profile
func (h *AuthHandler) GetProfile(c *gin.Context) {
	userID, exists := utils.GetCurrentUserID(c)
	if !exists {
		utils.ErrorResponse(c, http.StatusUnauthorized, "User not authenticated", nil)
		return
	}

	// This would typically use a user service to get the full profile
	// For now, we'll return the basic user info from the token
	claims, exists := utils.GetClaims(c)
	if !exists {
		utils.ErrorResponse(c, http.StatusUnauthorized, "User not authenticated", nil)
		return
	}

	user := &models.User{
		ID:    claims.UserID,
		Email: claims.Email,
		Role:  claims.Role,
	}

	utils.SuccessResponse(c, http.StatusOK, "Profile retrieved successfully", user)
}

// Logout handles user logout (client-side token removal)
func (h *AuthHandler) Logout(c *gin.Context) {
	// In a stateless JWT system, logout is typically handled client-side
	// by removing the token. However, we can implement token blacklisting
	// if needed for additional security.
	
	utils.SuccessResponse(c, http.StatusOK, "Logout successful", nil)
}

// ForgotPassword handles forgot password requests
func (h *AuthHandler) ForgotPassword(c *gin.Context) {
	var req models.ForgotPasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	// TODO: Implement forgot password logic
	// This would typically:
	// 1. Check if user exists
	// 2. Generate reset token
	// 3. Send email with reset link
	// 4. Store reset token with expiration

	utils.SuccessResponse(c, http.StatusOK, "Password reset email sent", gin.H{
		"message": "If an account with this email exists, a password reset link has been sent.",
	})
}

// ResetPassword handles password reset
func (h *AuthHandler) ResetPassword(c *gin.Context) {
	var req models.ResetPasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ErrorResponse(c, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	// TODO: Implement password reset logic
	// This would typically:
	// 1. Validate reset token
	// 2. Check token expiration
	// 3. Update user password
	// 4. Invalidate reset token

	utils.SuccessResponse(c, http.StatusOK, "Password reset successful", nil)
} 