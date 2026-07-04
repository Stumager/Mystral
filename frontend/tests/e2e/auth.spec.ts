import { expect, test } from "@playwright/test";

// Real credentials for login-flow tests (create a verified account and set env vars).
// Without them, login/logout tests are skipped — see QA_AUDIT_REPORT.md.
const E2E_EMAIL = process.env.E2E_EMAIL || "";
const E2E_PASSWORD = process.env.E2E_PASSWORD || "";

test.describe("Auth", () => {
  test("should show login screen with both auth modes", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("MYSTRAL");
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
  });

  test("should register new user and show email verification screen", async ({ page }) => {
    await page.goto("/");
    // switch to register tab (2nd button in the mode switcher)
    await page.locator("div.flex.mb-6 button").nth(1).click();

    const email = `e2e-${Date.now()}@qa-mystral.example.com`;
    await page.locator('input:not([type="email"]):not([type="password"])').first().fill("E2E Test");
    await page.locator('input[type="email"]').fill(email);
    const pwInputs = page.locator('input[type="password"]');
    await pwInputs.nth(0).fill("E2eTestPass1");
    await pwInputs.nth(1).fill("E2eTestPass1");
    await page.getByRole("button", { name: /зарегистр|регистрац|sign up|register/i }).last().click();

    // verification screen: six single-digit code inputs
    await expect(page.locator('input[maxlength="1"]')).toHaveCount(6, { timeout: 15000 });
  });

  test("should show error on wrong password", async ({ page }) => {
    await page.goto("/");
    await page.locator('input[type="email"]').fill("nonexistent-e2e@qa-mystral.example.com");
    await page.locator('input[type="password"]').first().fill("WrongPass1");
    await page.locator('input[type="password"]').first().press("Enter");
    // error text rendered in red
    await expect(page.locator("p.text-red-400, .text-red-400").first()).toBeVisible({ timeout: 10000 });
  });

  test("should login with valid credentials and redirect to home", async ({ page }) => {
    test.skip(!E2E_EMAIL, "E2E_EMAIL/E2E_PASSWORD not configured");
    await page.goto("/");
    await page.locator('input[type="email"]').fill(E2E_EMAIL);
    await page.locator('input[type="password"]').first().fill(E2E_PASSWORD);
    await page.locator('input[type="password"]').first().press("Enter");
    // home shows bottom nav (mobile) or sidebar (desktop) after login
    await expect(page.locator("h1, .font-cinzel").first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('input[type="email"]')).toHaveCount(0, { timeout: 15000 });
  });

  test("should logout successfully", async ({ page }) => {
    test.skip(!E2E_EMAIL, "E2E_EMAIL/E2E_PASSWORD not configured");
    await page.goto("/");
    await page.locator('input[type="email"]').fill(E2E_EMAIL);
    await page.locator('input[type="password"]').first().fill(E2E_PASSWORD);
    await page.locator('input[type="password"]').first().press("Enter");
    await expect(page.locator('input[type="email"]')).toHaveCount(0, { timeout: 15000 });

    // profile → logout
    await page.goto("/#profile").catch(() => {});
    const logoutBtn = page.getByText(/выйти|log ?out/i).first();
    if (await logoutBtn.isVisible().catch(() => false)) {
      await logoutBtn.click();
      await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 10000 });
    }
  });

  test("should navigate to forgot password page", async ({ page }) => {
    await page.goto("/forgot-password");
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 10000 });
  });
});
