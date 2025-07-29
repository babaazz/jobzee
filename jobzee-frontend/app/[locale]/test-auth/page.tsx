"use client";

import React, { useState } from "react";
import { authAPI } from "../../../lib/auth-api";

export default function TestAuthPage() {
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const testRegister = async () => {
    setLoading(true);
    setResult("Testing registration...");

    try {
      const response = await authAPI.register({
        email: `test${Date.now()}@example.com`,
        password: "password123",
        first_name: "Test",
        last_name: "User",
        role: "candidate",
      });

      setResult(
        `Registration successful: ${JSON.stringify(response, null, 2)}`
      );
    } catch (error: any) {
      setResult(`Registration failed: ${error.message}`);
      console.error("Registration error:", error);
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    setResult("Testing login...");

    try {
      const response = await authAPI.login({
        email: "test@example.com",
        password: "password123",
      });

      setResult(`Login successful: ${JSON.stringify(response, null, 2)}`);
    } catch (error: any) {
      setResult(`Login failed: ${error.message}`);
      console.error("Login error:", error);
    } finally {
      setLoading(false);
    }
  };

  const testDirectFetch = async () => {
    setLoading(true);
    setResult("Testing direct fetch...");

    try {
      const response = await fetch(
        "http://localhost:8080/api/v1/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: `direct${Date.now()}@example.com`,
            password: "password123",
            first_name: "Direct",
            last_name: "Test",
            role: "candidate",
          }),
        }
      );

      const data = await response.json();
      setResult(`Direct fetch result: ${JSON.stringify(data, null, 2)}`);
    } catch (error: any) {
      setResult(`Direct fetch failed: ${error.message}`);
      console.error("Direct fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Auth API Test</h1>

        <div className="space-y-4 mb-8">
          <button
            onClick={testRegister}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Test Registration
          </button>

          <button
            onClick={testLogin}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 ml-4"
          >
            Test Login
          </button>

          <button
            onClick={testDirectFetch}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 ml-4"
          >
            Test Direct Fetch
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Result:</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto max-h-96">
            {result || "Click a button to test..."}
          </pre>
        </div>
      </div>
    </div>
  );
}
