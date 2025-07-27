package kafka

import (
	"context"
	"encoding/json"
	"log"

	"github.com/segmentio/kafka-go"
)

type Producer struct {
	writer *kafka.Writer
}

type Event struct {
	Type    string      `json:"type"`
	Payload interface{} `json:"payload"`
	Timestamp int64     `json:"timestamp"`
}

func NewProducer(brokers []string, topic string) *Producer {
	writer := &kafka.Writer{
		Addr:     kafka.TCP(brokers...),
		Topic:    topic,
		Balancer: &kafka.LeastBytes{},
	}

	return &Producer{
		writer: writer,
	}
}

func (p *Producer) PublishEvent(ctx context.Context, event Event) error {
	eventBytes, err := json.Marshal(event)
	if err != nil {
		return err
	}

	err = p.writer.WriteMessages(ctx, kafka.Message{
		Value: eventBytes,
	})
	if err != nil {
		log.Printf("Failed to publish event: %v", err)
		return err
	}

	log.Printf("Published event: %s", event.Type)
	return nil
}

func (p *Producer) Close() error {
	return p.writer.Close()
} 