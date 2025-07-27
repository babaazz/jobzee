package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	"github.com/jobzee/multi-agent-backend/internal/api"
	"github.com/jobzee/multi-agent-backend/internal/config"
	"github.com/jobzee/multi-agent-backend/internal/middleware"
	"github.com/jobzee/multi-agent-backend/internal/repository"
	"github.com/jobzee/multi-agent-backend/internal/services"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Initialize database
	db, err := repository.NewDatabase(cfg)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize repositories
	jobRepo := repository.NewJobRepository(db.DB)
	candidateRepo := repository.NewCandidateRepository(db.DB)
	userRepo := repository.NewUserRepository(db.DB)

	// Initialize services
	jobService := services.NewJobService(cfg, jobRepo)
	candidateService := services.NewCandidateService(cfg, candidateRepo)
	agentService := services.NewAgentService(cfg)
	authService := services.NewAuthService(cfg, userRepo)

	// Initialize handlers
	handler := api.NewHandler(jobService, candidateService, agentService)
	authHandler := api.NewAuthHandler(authService)

	// Set Gin mode
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create router
	router := gin.Default()

	// Add middleware
	router.Use(middleware.CORSMiddleware())
	router.Use(middleware.LoggerMiddleware())

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "ok",
			"service": "api",
		})
	})

	// API routes
	apiGroup := router.Group("/api/v1")
	{
		// Auth routes (public)
		auth := apiGroup.Group("/auth")
		{
			auth.POST("/register", authHandler.Register)
			auth.POST("/login", authHandler.Login)
			auth.POST("/refresh", authHandler.RefreshToken)
			auth.POST("/forgot-password", authHandler.ForgotPassword)
			auth.POST("/reset-password", authHandler.ResetPassword)
		}

		// Protected routes
		protected := apiGroup.Group("/")
		protected.Use(middleware.AuthMiddleware(authService))
		{
			// User profile routes
			profile := protected.Group("/profile")
			{
				profile.GET("/", authHandler.GetProfile)
				profile.PUT("/", authHandler.UpdateProfile)
				profile.POST("/change-password", authHandler.ChangePassword)
				profile.POST("/logout", authHandler.Logout)
			}

			// Job routes
			jobs := protected.Group("/jobs")
			{
				jobs.GET("/", handler.GetJobs)
				jobs.GET("/:id", handler.GetJob)
				jobs.POST("/", handler.CreateJob)
			}

			// Candidate routes
			candidates := protected.Group("/candidates")
			{
				candidates.GET("/", handler.GetCandidates)
				candidates.GET("/:id", handler.GetCandidate)
				candidates.POST("/", handler.CreateCandidate)
			}

			// Agent routes
			agents := protected.Group("/agents")
			{
				agents.POST("/job-request", handler.ProcessJobRequest)
				agents.POST("/candidate-request", handler.ProcessCandidateRequest)
			}
		}
	}

	// Start server
	go func() {
		log.Printf("Starting API server on port %d", cfg.APIPort)
		if err := router.Run(fmt.Sprintf(":%d", cfg.APIPort)); err != nil {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down API server...")
} 