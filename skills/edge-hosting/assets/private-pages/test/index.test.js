import { test } from "node:test";
import assert from "node:assert/strict";
import { handle } from "../src/index.js";

const TEAM = "example.cloudflareaccess.com";
const AUD = "aud-tag-for-this-page";
const NAME = "0123456789abcdef01234567";
const NOW_MS = Date.UTC(2026, 9, 4, 12, 0, 0);
const NOW = Math.floor(NOW_MS / 1000);

const encoder = new TextEncoder();
const base64Url = (bytes) => Buffer.from(bytes).toString("base64url");

const keyPair = await crypto.subtle.generateKey(
  { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
  true,
  ["sign", "verify"],
);
const publicJwk = { ...(await crypto.subtle.exportKey("jwk", keyPair.publicKey)), kid: "kid-1", alg: "RS256" };

async function sign(payload, header = { alg: "RS256", kid: "kid-1", typ: "JWT" }) {
  const head = base64Url(encoder.encode(JSON.stringify(header)));
  const body = base64Url(encoder.encode(JSON.stringify(payload)));
  const signature = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", keyPair.privateKey, encoder.encode(`${head}.${body}`));
  return `${head}.${body}.${base64Url(new Uint8Array(signature))}`;
}

const validClaims = { iss: `https://${TEAM}`, aud: [AUD], email: "alex@example.org", sub: "user-1", exp: NOW + 600, nbf: NOW - 10 };

function kv(entries) {
  return { getWithMetadata: async (key) => entries[key] ?? { value: null, metadata: null } };
}

const certsFetch = async (url) => {
  assert.equal(url, `https://${TEAM}/cdn-cgi/access/certs`);
  return new Response(JSON.stringify({ keys: [publicJwk] }), { status: 200 });
};

const page = (metadata) => ({ [NAME]: { value: "<h1>briefing</h1>", metadata } });
const env = (entries) => ({ PAGES: kv(entries), ACCESS_TEAM_DOMAIN: TEAM });
const deps = { fetchImpl: certsFetch, now: () => NOW_MS };

async function get(path, entries, token) {
  const headers = token ? { "cf-access-jwt-assertion": token } : {};
  return handle(new Request(`https://share.example.org${path}`, { headers }), env(entries), deps);
}

test("serves the page to a request carrying a valid Access token for its audience", async () => {
  const response = await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }), await sign(validClaims));
  assert.equal(response.status, 200);
  assert.equal(await response.text(), "<h1>briefing</h1>");
  assert.equal(response.headers.get("cache-control"), "private, no-store");
  assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow");
});

test("rejects a token minted for another page's Access application", async () => {
  const token = await sign({ ...validClaims, aud: ["another-page"] });
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }), token)).status, 403);
});

test("rejects a request with no token, as when the Access app is missing or workers.dev is reachable", async () => {
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }))).status, 403);
});

test("rejects an expired token", async () => {
  const token = await sign({ ...validClaims, exp: NOW - 3600 });
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }), token)).status, 403);
});

test("rejects a token from another issuer", async () => {
  const token = await sign({ ...validClaims, iss: "https://evil.cloudflareaccess.com" });
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }), token)).status, 403);
});

test("rejects a tampered signature", async () => {
  const token = await sign(validClaims);
  const [head, , signature] = token.split(".");
  const forged = base64Url(encoder.encode(JSON.stringify({ ...validClaims, email: "mallory@example.org" })));
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }), `${head}.${forged}.${signature}`)).status, 403);
});

test("rejects a token signed with an algorithm other than RS256", async () => {
  const token = await sign(validClaims, { alg: "none", kid: "kid-1" });
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600, aud: AUD }), token)).status, 403);
});

test("answers 410 Gone once the page's expiry has passed", async () => {
  const response = await get(`/p/${NAME}`, page({ expires: NOW - 1, aud: AUD }), await sign(validClaims));
  assert.equal(response.status, 410);
});

test("treats a page uploaded without an Access audience as missing", async () => {
  assert.equal((await get(`/p/${NAME}`, page({ expires: NOW + 3600 }), await sign(validClaims))).status, 404);
});

test("treats a page without an expiry as missing", async () => {
  assert.equal((await get(`/p/${NAME}`, page({ aud: AUD }), await sign(validClaims))).status, 404);
});

test("answers only the exact page path", async () => {
  const token = await sign(validClaims);
  for (const path of ["/", `/p/${NAME}/`, `/p/${NAME.toUpperCase()}`, "/p/short", `/x/${NAME}`]) {
    assert.equal((await get(path, page({ expires: NOW + 3600, aud: AUD }), token)).status, 404, path);
  }
});

test("refuses methods other than GET and HEAD", async () => {
  const request = new Request(`https://share.example.org/p/${NAME}`, { method: "POST" });
  assert.equal((await handle(request, env(page({ expires: NOW + 3600, aud: AUD })), deps)).status, 405);
});
