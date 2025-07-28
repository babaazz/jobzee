"use client";

import React from "react";
import { Card } from "../ui/Card";
import { motion } from "framer-motion";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  maxWidth?: "sm" | "md" | "lg";
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  title,
  subtitle,
  maxWidth = "md",
}) => {
  const maxWidthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className={`w-full ${maxWidthClasses[maxWidth]}`}
      >
        <Card className="w-full">
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, duration: 0.3 }}
              className="mb-6"
            >
              <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center mx-auto">
                <span className="text-white text-2xl font-bold">J</span>
              </div>
            </motion.div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
            {subtitle && <p className="text-gray-600 text-sm">{subtitle}</p>}
          </div>
          {children}
        </Card>
      </motion.div>
    </div>
  );
};
