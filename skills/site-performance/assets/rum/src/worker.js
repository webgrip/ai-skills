const RATINGS = new Set(["good", "needs-improvement", "poor"]);
const MAX_BODY_BYTES = 8192;
const MAX_INDEX_BYTES = 96;
const MISSING = -1;

export const BLOBS = ["page", "device", "country", "navigation", "build", "lcp_rating", "inp_rating", "cls_rating", "lcp_target", "inp_target", "cls_target"];
export const DOUBLES = ["lcp", "inp", "cls", "fcp", "ttfb", "lcp_ttfb", "lcp_load_delay", "lcp_load_duration", "lcp_render_delay", "inp_input_delay", "inp_processing", "inp_presentation"];

const encoder = new TextEncoder();
const decoder = new TextDecoder();

export const truncateBytes = (text, limit) => {
  const bytes = encoder.encode(text);
  return bytes.length <= limit ? text : decoder.decode(bytes.slice(0, limit)).replace(/�+$/, "");
};

export const deviceClass = (request) => {
  const mobileHint = request.headers.get("sec-ch-ua-mobile");
  if (mobileHint) {
    return mobileHint === "?1" ? "mobile" : "desktop";
  }
  return /Mobi|Android|iPhone|iPad/i.test(request.headers.get("user-agent") ?? "") ? "mobile" : "desktop";
};

const measurement = (metrics, name) => {
  const metric = metrics?.[name];
  return metric && Number.isFinite(metric.value) && metric.value >= 0 && RATINGS.has(metric.rating) ? metric : null;
};

const valueOf = (metric) => (metric ? metric.value : MISSING);
const phase = (metric, index) => (metric && Number.isFinite(metric.phases?.[index]) ? metric.phases[index] : MISSING);
const text = (value, limit) => String(value ?? "").slice(0, limit);

export const dataPoint = (payload, request) => {
  if (typeof payload?.page !== "string" || typeof payload.metrics !== "object" || payload.metrics === null) {
    return null;
  }
  const [lcp, inp, cls, fcp, ttfb] = ["LCP", "INP", "CLS", "FCP", "TTFB"].map((name) => measurement(payload.metrics, name));
  if (![lcp, inp, cls, fcp, ttfb].some(Boolean)) {
    return null;
  }
  const page = truncateBytes(payload.page.split("?")[0], MAX_INDEX_BYTES);
  return {
    indexes: [page],
    blobs: [
      page, deviceClass(request), request.cf?.country ?? "XX", text(payload.navigation, 32), text(payload.build, 64),
      lcp?.rating ?? "", inp?.rating ?? "", cls?.rating ?? "",
      text(lcp?.target, 200), text(inp?.target, 200), text(cls?.target, 200),
    ],
    doubles: [
      valueOf(lcp), valueOf(inp), valueOf(cls), valueOf(fcp), valueOf(ttfb),
      phase(lcp, 0), phase(lcp, 1), phase(lcp, 2), phase(lcp, 3),
      phase(inp, 0), phase(inp, 1), phase(inp, 2),
    ],
  };
};

export const handleRum = async (request, env) => {
  if (request.method !== "POST") {
    return new Response(null, { status: 405 });
  }
  const body = await request.text();
  if (encoder.encode(body).length > MAX_BODY_BYTES) {
    return new Response(null, { status: 413 });
  }
  let payload;
  try {
    payload = JSON.parse(body);
  } catch {
    return new Response(null, { status: 400 });
  }
  const point = dataPoint(payload, request);
  if (point) {
    env.RUM.writeDataPoint(point);
  }
  return new Response(null, { status: 204 });
};

export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname === "/rum") {
      return handleRum(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};
