import { expect, test } from "@playwright/test";

test("home page shows ArchiveVet workbench", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Inspect nested archives");
  await expect(page.getByText("Drop an archive")).toBeVisible();
});
