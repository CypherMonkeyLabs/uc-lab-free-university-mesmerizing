import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  fullyParallel: false,
  retries: 0,
  workers: 1,
  timeout: 45000,
  use: {
    baseURL: "http://127.0.0.1:41731",
    launchOptions: process.env.PW_CHROME
      ? { executablePath: process.env.PW_CHROME, args: ["--no-sandbox"] }
      : { args: ["--no-sandbox"] },
  },
  webServer: {
    command: "python3 -m http.server 41731 --bind 127.0.0.1",
    url: "http://127.0.0.1:41731",
    reuseExistingServer: true,
    timeout: 20000,
  },
});
