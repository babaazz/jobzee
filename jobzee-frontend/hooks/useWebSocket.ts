import { useEffect, useRef, useState, useCallback } from "react";
import { useAuthStore } from "@/lib/auth-store";

interface WebSocketMessage {
  type: "message" | "status" | "error";
  data: any;
  timestamp: string;
}

interface UseWebSocketOptions {
  agentType: "job-finder" | "candidate-finder";
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export const useWebSocket = (options: UseWebSocketOptions) => {
  const { agentType, onMessage, onConnect, onDisconnect, onError } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const { user, accessToken } = useAuthStore();

  const connect = useCallback(() => {
    if (!user || !accessToken) {
      setError("User not authenticated");
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    // Determine WebSocket URL based on agent type
    const wsUrl =
      agentType === "job-finder"
        ? `ws://localhost:8084/ws/${user.id}`
        : `ws://localhost:8085/ws/${user.id}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttemptsRef.current = 0;
        onConnect?.();

        // Send authentication message
        ws.send(
          JSON.stringify({
            type: "auth",
            token: accessToken,
            userId: user.id,
          })
        );
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setIsConnecting(false);
        onDisconnect?.();

        // Attempt to reconnect if not a normal closure
        if (
          event.code !== 1000 &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttemptsRef.current),
            30000
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      ws.onerror = (event) => {
        setError("WebSocket connection error");
        onError?.(event);
      };
    } catch (err) {
      setError("Failed to create WebSocket connection");
      setIsConnecting(false);
    }
  }, [user, accessToken, agentType, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "User initiated disconnect");
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  const sendMessage = useCallback((message: string, sessionId?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = {
        message,
        session_id: sessionId || `session_${Date.now()}`,
        timestamp: new Date().toISOString(),
      };

      wsRef.current.send(JSON.stringify(payload));
      return true;
    } else {
      setError("WebSocket is not connected");
      return false;
    }
  }, []);

  const sendTypedMessage = useCallback((type: string, data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = {
        type,
        data,
        timestamp: new Date().toISOString(),
      };

      wsRef.current.send(JSON.stringify(payload));
      return true;
    } else {
      setError("WebSocket is not connected");
      return false;
    }
  }, []);

  // Auto-connect when user is authenticated
  useEffect(() => {
    if (user && accessToken) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [user, accessToken, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isConnecting,
    lastMessage,
    error,
    sendMessage,
    sendTypedMessage,
    connect,
    disconnect,
  };
};
