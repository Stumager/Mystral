import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30000,
  fullyParallel: false, // sequential — register/login hit per-IP rate limits
  retries: 1,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL || "https://mystral.space",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] }, testIgnore: /mobile\.spec\.ts/ },
    { name: "firefox", use: { ...devices["Desktop Firefox"] }, testIgnore: /mobile\.spec\.ts/ },
    { name: "webkit", use: { ...devices["Desktop Safari"] }, testIgnore: /mobile\.spec\.ts/ },
    { name: "mobile", use: { ...devices["iPhone 14"] }, testMatch: /mobile\.spec\.ts/ },
  ],
});
