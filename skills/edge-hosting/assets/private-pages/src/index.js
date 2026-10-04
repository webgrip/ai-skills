const PAGE_PATH = /^\/p\/([a-f0-9]{24})$/;
const CERTS_TTL_MS = 60 * 60 * 1000;
const CLOCK_SKEW_SECONDS = 60;

const PAGE_HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "cache-control": "private, no-store",
  "x-robots-tag": "noindex, nofollow",
  "referrer-policy": "no-referrer",
  "x-content-type-options": "nosniff",
  "content-security-policy": "frame-ancestors 'none'",
};

const certsByTeam = new Map();

function plain(status, body) {
  return new Response(body, {
    status,
    headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "private, no-store" },
  });
}

function base64UrlToBytes(segment) {
  const base64 = segment.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(segment.length / 4) * 4, "=");
  return Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
}

function decodeSegment(segment) {
  return JSON.parse(new TextDecoder().decode(base64UrlToBytes(segment)));
}

async function signingKeys(teamDomain, fetchImpl, now, forceRefresh) {
  const cached = certsByTeam.get(teamDomain);
  if (cached && !forceRefresh && now() - cached.fetchedAt < CERTS_TTL_MS) return cached.keys;
  const response = await fetchImpl(`https://${teamDomain}/cdn-cgi/access/certs`);
  if (!response.ok) throw new Error(`certs fetch failed: ${response.status}`);
  const { keys } = await response.json();
  certsByTeam.set(teamDomain, { keys, fetchedAt: now() });
  return keys;
}

async function findKey(teamDomain, kid, fetchImpl, now) {
  const fresh = await signingKeys(teamDomain, fetchImpl, now, false);
  return fresh.find((k) => k.kid === kid) ?? (await signingKeys(teamDomain, fetchImpl, now, true)).find((k) => k.kid === kid);
}

export async function verifyAccessJwt(token, { teamDomain, audience, fetchImpl = fetch, now = Date.now }) {
  const parts = token?.split(".") ?? [];
  if (parts.length !== 3) return null;
  const [headerPart, payloadPart, signaturePart] = parts;
  let header;
  let payload;
  try {
    header = decodeSegment(headerPart);
    payload = decodeSegment(payloadPart);
  } catch {
    return null;
  }
  if (header.alg !== "RS256" || !header.kid) return null;

  const jwk = await findKey(teamDomain, header.kid, fetchImpl, now);
  if (!jwk) return null;
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const signed = new TextEncoder().encode(`${headerPart}.${payloadPart}`);
  const valid = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, base64UrlToBytes(signaturePart), signed);
  if (!valid) return null;

  const nowSeconds = now() / 1000;
  const audiences = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (payload.iss !== `https://${teamDomain}`) return null;
  if (!audiences.includes(audience)) return null;
  if (typeof payload.exp !== "number" || payload.exp + CLOCK_SKEW_SECONDS < nowSeconds) return null;
  if (typeof payload.nbf === "number" && payload.nbf - CLOCK_SKEW_SECONDS > nowSeconds) return null;
  return { email: payload.email ?? null, subject: payload.sub ?? null };
}

export async function handle(request, env, deps = {}) {
  const now = deps.now ?? Date.now;
  if (request.method !== "GET" && request.method !== "HEAD") return plain(405, "Method not allowed");
  const match = new URL(request.url).pathname.match(PAGE_PATH);
  if (!match) return plain(404, "Not found");

  const { value, metadata } = await env.PAGES.getWithMetadata(match[1]);
  const expires = Number(metadata?.expires);
  if (!value || !expires || !metadata?.aud) return plain(404, "Not found");

  const identity = await verifyAccessJwt(request.headers.get("cf-access-jwt-assertion"), {
    teamDomain: env.ACCESS_TEAM_DOMAIN,
    audience: metadata.aud,
    fetchImpl: deps.fetchImpl ?? fetch,
    now,
  });
  if (!identity) return plain(403, "Forbidden");

  if (now() / 1000 > expires) return plain(410, "This link has expired. Ask whoever sent it for a new one.");

  return new Response(request.method === "HEAD" ? null : value, { headers: PAGE_HEADERS });
}

export default {
  fetch: (request, env) => handle(request, env),
};
