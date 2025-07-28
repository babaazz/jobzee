package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	"github.com/jobzee/jobzee-backend/internal/config"
	"github.com/jobzee/jobzee-backend/internal/services"
	pb "github.com/jobzee/jobzee-backend/proto/proto/agent_service"
)

type agentServer struct {
	pb.UnimplementedAgentServiceServer
	agentService *services.AgentService
}

func (s *agentServer) ProcessJobRequest(ctx context.Context, req *pb.JobRequest) (*pb.JobResponse, error) {
	return s.agentService.ProcessJobRequest(ctx, req)
}

func (s *agentServer) ProcessCandidateRequest(ctx context.Context, req *pb.CandidateRequest) (*pb.CandidateResponse, error) {
	return s.agentService.ProcessCandidateRequest(ctx, req)
}

func main() {
	cfg := config.Load()

	// Initialize services
	agentService := services.NewAgentService(cfg)

	// Create gRPC server
	server := grpc.NewServer()
	pb.RegisterAgentServiceServer(server, &agentServer{
		agentService: agentService,
	})

	// Enable reflection for debugging
	reflection.Register(server)

	// Start server
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", cfg.AgentServicePort))
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	log.Printf("Agent service starting on port %d", cfg.AgentServicePort)

	go func() {
		if err := server.Serve(lis); err != nil {
			log.Fatalf("Failed to serve: %v", err)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down agent service...")
	server.GracefulStop()
} 