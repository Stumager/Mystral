import { expect, test, Page } from "@playwright/test";

const E2E_EMAIL = process.env.E2E_EMAIL || "";
const E2E_PASSWORD = process.env.E2E_PASSWORD || "";

async function login(page: Page) {
  await page.goto("/");
  await page.locator('input[type="email"]').fill(E2E_EMAIL);
  await page.locator('input[type="password"]').first().fill(E2E_PASSWORD);
  await page.locator('input[type="password"]').first().press("Enter");
  await expect(page.locator('input[type="email"]')).toHaveCount(0, { timeout: 15000 });
}

test.describe("Navigation (authenticated)", () => {
  test.skip(!E2E_EMAIL, "E2E_EMAIL/E2E_PASSWORD not configured");

  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  const sections: [string, RegExp][] = [
    ["tarot", /таро|tarot/i],
    ["moon", /луна|лунн|moon|lunar/i],
    ["compatibility", /совместим|compat/i],
    ["natal", /натальн|natal/i],
    ["numerology", /нумеролог|numerolog/i],
    ["runes", /руны|runes/i],
    ["profile", /профиль|profile/i],
  ];

  for (const [section, pattern] of sections) {
    test(`should navigate to ${section} section`, async ({ page }) => {
      const link = page.getByText(pattern).first();
      await link.click();
      await expect(page.locator("body")).toContainText(pattern, { timeout: 10000 });
    });
  }

  test("should show home page content after login", async ({ page }) => {
    await expect(page.locator("body")).toContainText(/гороскоп|horoscope|лунный|lunar/i, { timeout: 15000 });
  });
});

test.describe("Public pages do not require auth", () => {
  test("privacy page loads without auth", async ({ page }) => {
    await page.goto("/privacy");
    await expect(page.locator("body")).toContainText(/конфиденциальн|privacy/i);
  });

  test("terms page loads without auth", async ({ page }) => {
    await page.goto("/terms");
    await expect(page.locator("body")).toContainText(/оферта|соглашение|terms/i);
  });
});
