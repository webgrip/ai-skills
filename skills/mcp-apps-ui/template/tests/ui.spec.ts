import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { TOOL_NAMES } from "../src/contract.ts";

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

async function openHost(page: Page, query: Record<string, string>) {
  const outbound: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!["127.0.0.1", "localhost"].includes(url.hostname) && url.protocol !== "data:" && url.protocol !== "about:") outbound.push(request.url());
  });
  await page.goto(`/harness.html?${new URLSearchParams(query)}`);
  const view = page.frameLocator("#view");
  await expect.poll(() => page.evaluate(() => window.hostState.initialized)).toBe(true);
  return { view, outbound };
}

const matrix = [
  { profile: "full", theme: "light", locale: "en-US", state: "Healthy", date: "Nov 20, 2026" },
  { profile: "full", theme: "dark", locale: "de-DE", state: "Fehlerfrei", date: "20.11.2026" },
  { profile: "minimal", theme: "light", locale: "en-US", state: "Healthy", date: "Nov 20, 2026" },
  { profile: "minimal", theme: "dark", locale: "en-US", state: "Healthy", date: "Nov 20, 2026" },
];

for (const row of matrix) {
  test(`${row.profile} host, ${row.theme}, ${row.locale}: renders, fits, passes axe`, async ({ page }) => {
    const { view, outbound } = await openHost(page, { profile: row.profile, theme: row.theme, locale: row.locale });
    await expect(view.getByRole("heading", { name: "Checkout API" })).toBeVisible();
    await expect(view.getByText(row.state, { exact: true })).toBeVisible();
    await expect(view.locator("time")).toContainText(row.date);
    await expect.poll(() => page.evaluate(() => window.hostState.height ?? 0)).toBeGreaterThan(80);
    const frame = page.frame({ url: /about:srcdoc/ })!;
    const overflow = await frame.evaluate(() => ({
      vertical: document.documentElement.scrollHeight - window.innerHeight,
      horizontal: document.documentElement.scrollWidth - window.innerWidth,
    }));
    expect(overflow.vertical).toBeLessThanOrEqual(1);
    expect(overflow.horizontal).toBeLessThanOrEqual(0);
    const results = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
    expect(results.violations.map((violation) => `${violation.id}: ${violation.nodes.map((node) => node.target.join(" ")).join(", ")}`)).toEqual([]);
    await expect(page.locator("#view")).toHaveScreenshot(`card-${row.profile}-${row.theme}-${row.locale}.png`);
    expect(outbound).toEqual([]);
  });
}

test("host style variables win over the fallback tokens", async ({ page }) => {
  const { view } = await openHost(page, { profile: "full" });
  await expect(view.getByRole("heading", { name: "Checkout API" })).toBeVisible();
  const frame = page.frame({ url: /about:srcdoc/ })!;
  expect(await frame.evaluate(() => getComputedStyle(document.body).fontFamily)).toContain("Georgia");
});

test("without host variables the fallback tokens apply", async ({ page }) => {
  const { view } = await openHost(page, { profile: "minimal" });
  await expect(view.getByRole("heading", { name: "Checkout API" })).toBeVisible();
  const frame = page.frame({ url: /about:srcdoc/ })!;
  expect(await frame.evaluate(() => getComputedStyle(document.body).fontFamily)).toContain("system-ui");
});

test("a host without server tools gets no action buttons and a chat hint", async ({ page }) => {
  const { view } = await openHost(page, { profile: "minimal" });
  await expect(view.getByText("Ask in the chat to change this service.")).toBeVisible();
  await expect(view.getByRole("button")).toHaveCount(0);
});

test("restart is a two-step, keyboard-reachable flow with an idempotency key", async ({ page }) => {
  const { view } = await openHost(page, { profile: "full" });
  const restart = view.getByRole("button", { name: "Restart" });
  const box = await restart.boundingBox();
  expect(box!.height).toBeGreaterThanOrEqual(44);
  await restart.focus();
  await page.keyboard.press("Enter");
  const confirm = view.getByRole("button", { name: "Confirm restart" });
  await expect(confirm).toBeFocused();
  await expect(view.getByRole("status")).toContainText("Restart all 3 replicas");
  await page.keyboard.press("Enter");
  await expect(view.getByRole("status")).toHaveText("Restart accepted");
  const calls = await page.evaluate(() => window.hostLog);
  const toolCalls = calls.filter((entry) => entry.method === "tools/call") as Array<{ params: { name: string; arguments: Record<string, string> } }>;
  expect(toolCalls.map((call) => call.params.name)).toEqual([TOOL_NAMES.prepareRestart, TOOL_NAMES.confirmRestart]);
  expect(toolCalls[1].params.arguments.idempotencyKey).toMatch(/^[0-9a-f]{32}$/);
  expect(calls.some((entry) => entry.method === "ui/update-model-context")).toBe(true);
});

test("cancel returns focus to the restart button and calls nothing", async ({ page }) => {
  const { view } = await openHost(page, { profile: "full" });
  await view.getByRole("button", { name: "Restart" }).click();
  await view.getByRole("button", { name: "Cancel" }).click();
  await expect(view.getByRole("button", { name: "Restart" })).toBeFocused();
  const names = await page.evaluate(() => window.hostLog.map((entry) => entry.method));
  expect(names).toEqual(["tools/call"]);
});

test("a service the caller may not restart shows why instead of a button", async ({ page }) => {
  const { view } = await openHost(page, { profile: "full", fixture: "degraded", width: "320" });
  await expect(view.getByText("You cannot restart this service from here.")).toBeVisible();
  await expect(view.getByRole("button")).toHaveCount(0);
  const frame = page.frame({ url: /about:srcdoc/ })!;
  expect(await frame.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBeLessThanOrEqual(0);
});

for (const result of ["malformed", "text-only"]) {
  test(`a ${result} result degrades to a pointer at the text answer`, async ({ page }) => {
    const { view } = await openHost(page, { profile: "full", result });
    await expect(view.getByText("The text answer above has the details.", { exact: false })).toBeVisible();
  });
}

test("the loading skeleton stops animating under reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const { view } = await openHost(page, { profile: "minimal", result: "none" });
  await expect(view.locator(".skeleton span").first()).toBeAttached();
  const frame = page.frame({ url: /about:srcdoc/ })!;
  expect(await frame.evaluate(() => getComputedStyle(document.querySelector(".skeleton span")!).animationName)).toBe("none");
});
