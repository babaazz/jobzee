const fetch = require("node-fetch");

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1";

async function testAPI() {
  console.log("Testing API connectivity...");
  console.log("API URL:", API_BASE_URL);

  try {
    // Test health endpoint
    const healthResponse = await fetch(
      `${API_BASE_URL.replace("/api/v1", "")}/health`
    );
    console.log("Health check status:", healthResponse.status);

    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log("Health check response:", healthData);
    }

    // Test auth endpoints
    const testUser = {
      email: "test@example.com",
      password: "password123",
      firstName: "Test",
      lastName: "User",
      role: "candidate",
    };

    console.log("\nTesting registration...");
    const registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(testUser),
    });

    console.log("Registration status:", registerResponse.status);
    const registerData = await registerResponse.json();
    console.log("Registration response:", registerData);

    if (registerResponse.ok) {
      console.log("\nTesting login...");
      const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: testUser.email,
          password: testUser.password,
        }),
      });

      console.log("Login status:", loginResponse.status);
      const loginData = await loginResponse.json();
      console.log("Login response:", loginData);
    }
  } catch (error) {
    console.error("API test failed:", error.message);
  }
}

testAPI();
