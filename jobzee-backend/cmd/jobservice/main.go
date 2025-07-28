package main

import (
	"log"
	"net"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	"github.com/jobzee/jobzee-backend/internal/config"
	"github.com/jobzee/jobzee-backend/internal/database"
	"github.com/jobzee/jobzee-backend/internal/services/jobservice"
	pb "github.com/jobzee/jobzee-backend/proto/proto/job_service"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Initialize database
	db, err := database.NewConnection(cfg.Database)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create gRPC server
	server := grpc.NewServer()

	// Register services
	jobService := jobservice.NewJobService(db)
	pb.RegisterJobServiceServer(server, jobService)

	// Register reflection service for development
	reflection.Register(server)

	// Start listening
	port := "9090"
	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	log.Printf("Starting Job Service gRPC server on port %s", port)
	if err := server.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
} 