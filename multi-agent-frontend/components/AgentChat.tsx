"use client";

import React, { useState, useRef, useEffect } from "react";
import { useTranslations } from "next-intl";

interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: Date;
  metadata?: {
    type?: "text" | "question" | "suggestion" | "match";
    data?: any;
  };
}

interface AgentChatProps {
  agentType: "job-finder" | "candidate-finder";
  userId: string;
  initialMessage?: string;
  onProfileComplete?: (profile: any) => void;
  onMatchFound?: (match: any) => void;
}

export default function AgentChat({
  agentType,
  userId,
  initialMessage,
  onProfileComplete,
  onMatchFound,
}: AgentChatProps) {
  const t = useTranslations("AgentChat");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize chat with welcome message
  useEffect(() => {
    const welcomeMessage =
      agentType === "job-finder"
        ? t("jobFinderWelcome")
        : t("candidateFinderWelcome");

    setMessages([
      {
        id: "welcome",
        role: "agent",
        content: welcomeMessage,
        timestamp: new Date(),
        metadata: { type: "text" },
      },
    ]);

    if (initialMessage) {
      handleSendMessage(initialMessage);
    }
  }, [agentType, initialMessage, t]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev: Message[]) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await sendMessageToAgent(content);
      handleAgentResponse(response);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "agent",
        content: t("errorMessage"),
        timestamp: new Date(),
        metadata: { type: "text" },
      };
      setMessages((prev: Message[]) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const sendMessageToAgent = async (content: string) => {
    const endpoint =
      agentType === "job-finder"
        ? "/api/agents/job-finder/chat"
        : "/api/agents/candidate-finder/chat";

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        userId,
        message: content,
        agentType,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to send message");
    }

    return response.json();
  };

  const handleAgentResponse = (response: any) => {
    const { message, type, data, profileComplete, matchFound } = response;

    const agentMessage: Message = {
      id: Date.now().toString(),
      role: "agent",
      content: message,
      timestamp: new Date(),
      metadata: { type, data },
    };

    setMessages((prev: Message[]) => [...prev, agentMessage]);

    // Handle profile completion
    if (profileComplete && onProfileComplete) {
      onProfileComplete(data);
    }

    // Handle match found
    if (matchFound && onMatchFound) {
      onMatchFound(data);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    }
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === "user";
    const messageType = message.metadata?.type;

    return (
      <div
        key={message.id}
        className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
      >
        <div
          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
            isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
          }`}
        >
          <div className="text-sm">{message.content}</div>

          {/* Render special message types */}
          {messageType === "question" && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="text-xs text-gray-500">{t("questionPrompt")}</div>
            </div>
          )}

          {messageType === "suggestion" && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="text-xs text-gray-500">
                {t("suggestionPrompt")}
              </div>
            </div>
          )}

          {messageType === "match" && message.metadata?.data && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <MatchCard match={message.metadata.data} />
            </div>
          )}

          <div
            className={`text-xs mt-1 ${
              isUser ? "text-blue-100" : "text-gray-500"
            }`}
          >
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div
            className={`w-3 h-3 rounded-full ${
              agentType === "job-finder" ? "bg-green-500" : "bg-blue-500"
            }`}
          />
          <div>
            <h3 className="font-semibold text-gray-900">
              {agentType === "job-finder"
                ? t("jobFinderTitle")
                : t("candidateFinderTitle")}
            </h3>
            <p className="text-sm text-gray-500">
              {agentType === "job-finder"
                ? t("jobFinderSubtitle")
                : t("candidateFinderSubtitle")}
            </p>
          </div>
        </div>

        {isTyping && (
          <div className="flex items-center space-x-1">
            <div className="text-sm text-gray-500">{t("typing")}</div>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div
                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style={{ animationDelay: "0.1s" }}
              />
              <div
                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style={{ animationDelay: "0.2s" }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(renderMessage)}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={t("inputPlaceholder")}
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          <button
            onClick={() => handleSendMessage(inputValue)}
            disabled={isLoading || !inputValue.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              t("send")
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// Match Card Component
interface MatchCardProps {
  match: {
    id: string;
    title: string;
    company: string;
    location: string;
    matchScore: number;
    reasoning: string;
    skillsMatch: string[];
    missingSkills: string[];
  };
}

function MatchCard({ match }: MatchCardProps) {
  const t = useTranslations("AgentChat");

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h4 className="font-semibold text-gray-900">{match.title}</h4>
          <p className="text-sm text-gray-600">{match.company}</p>
          <p className="text-xs text-gray-500">{match.location}</p>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-green-600">
            {Math.round(match.matchScore * 100)}%
          </div>
          <div className="text-xs text-gray-500">{t("matchScore")}</div>
        </div>
      </div>

      <p className="text-sm text-gray-700 mb-2">{match.reasoning}</p>

      {match.skillsMatch.length > 0 && (
        <div className="mb-2">
          <div className="text-xs font-medium text-gray-600 mb-1">
            {t("matchingSkills")}:
          </div>
          <div className="flex flex-wrap gap-1">
            {match.skillsMatch.slice(0, 3).map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {match.missingSkills.length > 0 && (
        <div>
          <div className="text-xs font-medium text-gray-600 mb-1">
            {t("missingSkills")}:
          </div>
          <div className="flex flex-wrap gap-1">
            {match.missingSkills.slice(0, 2).map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-3 flex space-x-2">
        <button className="flex-1 px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors">
          {t("viewDetails")}
        </button>
        <button className="flex-1 px-3 py-1 bg-gray-200 text-gray-800 text-xs rounded hover:bg-gray-300 transition-colors">
          {t("apply")}
        </button>
      </div>
    </div>
  );
}
