import assert from "node:assert/strict";
import { test } from "node:test";
import worker, { BLOBS, DOUBLES, dataPoint, deviceClass, handleRum, truncateBytes } from "../src/worker.js";

const request = (body, headers = {}, method = "POST") =>
  Object.assign(new Request("https://example.org/rum", { method, headers, body: method === "POST" ? body : undefined }), {
    cf: { country: "NL" },
  });

const recorder = () => {
  const points = [];
  return { points, env: { RUM: { writeDataPoint: (point) => points.push(point) }, ASSETS: { fetch: () => new Response("asset") } } };
};

const column = (point, names, name) => point[names === BLOBS ? "blobs" : "doubles"][names.indexOf(name)];

test("one page view becomes one data point, indexed by page template", async () => {
  const { points, env } = recorder();
  const payload = {
    page: "/events?ref=x",
    build: "2026-10-04.3",
    navigation: "navigate",
    metrics: {
      LCP: { value: 2100, rating: "good", target: "main>img", phases: [300, 200, 900, 700] },
      INP: { value: 180, rating: "good", target: "button.menu", phases: [20, 120, 40] },
      CLS: { value: 0.02, rating: "good", target: "" },
    },
  };
  const response = await handleRum(request(JSON.stringify(payload), { "sec-ch-ua-mobile": "?1" }), env);
  assert.equal(response.status, 204);
  assert.equal(points.length, 1);
  const [point] = points;
  assert.deepEqual(point.indexes, ["/events"]);
  assert.equal(column(point, BLOBS, "device"), "mobile");
  assert.equal(column(point, BLOBS, "country"), "NL");
  assert.equal(column(point, BLOBS, "build"), "2026-10-04.3");
  assert.equal(column(point, DOUBLES, "lcp"), 2100);
  assert.equal(column(point, DOUBLES, "lcp_load_delay"), 200);
  assert.equal(column(point, DOUBLES, "inp_processing"), 120);
  assert.equal(column(point, DOUBLES, "fcp"), -1);
  assert.ok(point.blobs.length <= 20 && point.doubles.length <= 20);
});

test("invalid metrics are dropped and an empty page view writes nothing", async () => {
  const { points, env } = recorder();
  const payload = { page: "/", metrics: { FID: { value: 10, rating: "good" }, INP: { value: 120, rating: "excellent" }, LCP: { value: -5, rating: "good" } } };
  assert.equal(dataPoint(payload, request("{}")), null);
  await handleRum(request(JSON.stringify(payload)), env);
  assert.equal(points.length, 0);
});

test("oversized, malformed and non-POST requests are refused", async () => {
  const { env } = recorder();
  assert.equal((await handleRum(request("x".repeat(9000)), env)).status, 413);
  assert.equal((await handleRum(request("{not json"), env)).status, 400);
  assert.equal((await handleRum(request(null, {}, "GET"), env)).status, 405);
});

test("index stays within 96 bytes for multi-byte paths", () => {
  assert.ok(new TextEncoder().encode(truncateBytes("/" + "é".repeat(80), 96)).length <= 96);
});

test("device class falls back to the user agent", () => {
  assert.equal(deviceClass(request("{}", { "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)" })), "mobile");
  assert.equal(deviceClass(request("{}", { "user-agent": "Mozilla/5.0 (X11; Linux x86_64)" })), "desktop");
});

test("other paths fall through to static assets", async () => {
  const { env } = recorder();
  assert.equal(await (await worker.fetch(new Request("https://example.org/about"), env)).text(), "asset");
});
