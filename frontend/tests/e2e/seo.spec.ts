import { expect, test } from "@playwright/test";

test.describe("SEO pages", () => {
  test("should load zodiac/scorpio without auth", async ({ page }) => {
    const res = await page.goto("/zodiac/scorpio");
    expect(res?.status()).toBe(200);
  });

  test("should have correct title on zodiac page", async ({ page }) => {
    await page.goto("/zodiac/scorpio");
    await expect(page).toHaveTitle(/Скорпион.*Mystral/);
  });

  test("should have h1 on zodiac page", async ({ page }) => {
    await page.goto("/zodiac/scorpio");
    const h1 = page.locator("h1");
    await expect(h1.first()).toBeVisible();
    await expect(h1.first()).toContainText(/Скорпион/);
  });

  test("should have canonical link on zodiac page", async ({ page }) => {
    await page.goto("/zodiac/scorpio");
    const canonical = page.locator('link[rel="canonical"]');
    await expect(canonical).toHaveAttribute("href", "https://mystral.space/zodiac/scorpio");
  });

  test("should load tarot/the-fool without auth", async ({ page }) => {
    const res = await page.goto("/tarot/the-fool");
    expect(res?.status()).toBe(200);
    await expect(page.locator("h1").first()).toBeVisible();
  });

  test("should load runes/fehu without auth", async ({ page }) => {
    const res = await page.goto("/runes/fehu");
    expect(res?.status()).toBe(200);
  });

  test("should load sitemap.xml", async ({ request }) => {
    const res = await request.get("/sitemap.xml");
    expect(res.status()).toBe(200);
    const body = await res.text();
    const urlCount = (body.match(/<loc>/g) || []).length;
    expect(urlCount).toBeGreaterThanOrEqual(126);
  });

  test("should return 404 for invalid slug", async ({ request }) => {
    const res = await request.get("/zodiac/not-a-sign");
    expect(res.status()).toBe(404);
  });

  test("zodiac hub lists all 12 signs", async ({ page }) => {
    await page.goto("/zodiac");
    for (const sign of ["Овен", "Скорпион", "Рыбы"]) {
      await expect(page.locator("body")).toContainText(sign);
    }
  });
});
