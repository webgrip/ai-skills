import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  reporter: process.env.CI ? "github" : "list",
  updateSnapshots: "missing",
  expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.01 } },
  use: { baseURL: "http://127.0.0.1:4173", ...devices["Desktop Chrome"] },
  webServer: {
    command: "npm run harness -- --host 127.0.0.1",
    url: "http://127.0.0.1:4173/harness.html",
    reuseExistingServer: !process.env.CI,
  },
});
