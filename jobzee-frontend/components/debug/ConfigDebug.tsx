"use client";

import React from "react";

export const ConfigDebug: React.FC = () => {
  const config = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NODE_ENV: process.env.NODE_ENV,
    API_BASE_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1",
  };

  return (
    <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
      <h3 className="font-bold mb-2">Debug Configuration:</h3>
      <pre className="text-sm">{JSON.stringify(config, null, 2)}</pre>
    </div>
  );
};
