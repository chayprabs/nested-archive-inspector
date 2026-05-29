import path from "node:path";
import { expect, test } from "@playwright/test";

const samplesDir = path.join(process.cwd(), "public", "samples");

test("diff mode compares release archives", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/");
  await page.getByRole("button", { name: "Diff two archives" }).click();

  const leftChooser = page.waitForEvent("filechooser");
  await page.getByText("Drop left archive").click();
  const leftPicker = await leftChooser;
  await leftPicker.setFiles(path.join(samplesDir, "release-1.2.0.tar.gz"));

  const rightChooser = page.waitForEvent("filechooser");
  await page.getByText("Drop right archive").click();
  const rightPicker = await rightChooser;
  await rightPicker.setFiles(path.join(samplesDir, "release-1.3.0.tar.gz"));

  await page.getByRole("button", { name: "Run diff" }).click();
  await expect(page.getByText(/Diff — .* added/)).toBeVisible({ timeout: 60_000 });
});
