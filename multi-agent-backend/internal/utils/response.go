package utils

import (
	"github.com/gin-gonic/gin"
	"github.com/jobzee/multi-agent-backend/internal/models"
)

// SuccessResponse sends a standardized success response
func SuccessResponse(c *gin.Context, statusCode int, message string, data interface{}) {
	c.JSON(statusCode, gin.H{
		"success": true,
		"message": message,
		"data":    data,
	})
}

// ErrorResponse sends a standardized error response
func ErrorResponse(c *gin.Context, statusCode int, message string, err error) {
	response := gin.H{
		"success": false,
		"message": message,
	}

	if err != nil {
		response["error"] = err.Error()
	}

	c.JSON(statusCode, response)
}

// GetCurrentUserID gets the current user ID from context
func GetCurrentUserID(c *gin.Context) (uint, bool) {
	userID, exists := c.Get("user_id")
	if !exists {
		return 0, false
	}
	return userID.(uint), true
}

// GetCurrentUserRole gets the current user role from context
func GetCurrentUserRole(c *gin.Context) (models.UserRole, bool) {
	userRole, exists := c.Get("user_role")
	if !exists {
		return "", false
	}
	return userRole.(models.UserRole), true
}

// GetCurrentUserEmail gets the current user email from context
func GetCurrentUserEmail(c *gin.Context) (string, bool) {
	userEmail, exists := c.Get("user_email")
	if !exists {
		return "", false
	}
	return userEmail.(string), true
}

// GetClaims gets the JWT claims from context
func GetClaims(c *gin.Context) (*models.Claims, bool) {
	claims, exists := c.Get("claims")
	if !exists {
		return nil, false
	}
	return claims.(*models.Claims), true
} 