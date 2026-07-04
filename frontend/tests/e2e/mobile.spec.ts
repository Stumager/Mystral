import { expect, test } from "@playwright/test";

// Runs only in the "mobile" project (iPhone 14 viewport 390x844, WebKit)

test.describe("Mobile viewport", () => {
  test("login screen fits mobile viewport", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("MYSTRAL");
    const emailBox = await page.locator('input[type="email"]').boundingBox();
    expect(emailBox).not.toBeNull();
    expect(emailBox!.width).toBeLessThanOrEqual(390);
  });

  test("no horizontal scroll on login", async ({ page }) => {
    await page.goto("/");
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(1);
  });

  test("zodiac SEO page renders on mobile", async ({ page }) => {
    await page.goto("/zodiac/scorpio");
    await expect(page.locator("h1").first()).toBeVisible();
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(1);
  });

  test("tarot SEO page renders on mobile", async ({ page }) => {
    await page.goto("/tarot/the-fool");
    await expect(page.locator("h1").first()).toBeVisible();
  });

  test("privacy page readable on mobile", async ({ page }) => {
    await page.goto("/privacy");
    await expect(page.locator("body")).toContainText(/конфиденциальн|privacy/i);
  });

  test("should show bottom nav on mobile after login", async ({ page }) => {
    test.skip(!process.env.E2E_EMAIL, "E2E_EMAIL/E2E_PASSWORD not configured");
    await page.goto("/");
    await page.locator('input[type="email"]').fill(process.env.E2E_EMAIL!);
    await page.locator('input[type="password"]').first().fill(process.env.E2E_PASSWORD!);
    await page.locator('input[type="password"]').first().press("Enter");
    await expect(page.locator('input[type="email"]')).toHaveCount(0, { timeout: 15000 });
    // BottomNav is fixed at the bottom on mobile
    const nav = page.locator("nav, [class*=bottom]").last();
    await expect(nav).toBeVisible();
  });
});
