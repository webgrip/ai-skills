import { onCLS, onFCP, onINP, onLCP, onTTFB } from "web-vitals/attribution";

const endpoint = "/rum";
const pending = {};

const pageGroup = () => document.documentElement.dataset.template || location.pathname;
const buildId = () => document.documentElement.dataset.build || "";

const attributionTarget = ({ attribution }) =>
  attribution?.target ?? attribution?.interactionTarget ?? attribution?.largestShiftTarget ?? "";

const phases = ({ name, attribution }) => {
  if (name === "LCP" && attribution) {
    return [attribution.timeToFirstByte, attribution.resourceLoadDelay, attribution.resourceLoadDuration, attribution.elementRenderDelay];
  }
  if (name === "INP" && attribution) {
    return [attribution.inputDelay, attribution.processingDuration, attribution.presentationDelay];
  }
  return [];
};

const record = (metric) => {
  pending.navigation = metric.navigationType;
  pending[metric.name] = {
    value: metric.value,
    rating: metric.rating,
    target: attributionTarget(metric).slice(0, 200),
    phases: phases(metric).map((phase) => Math.round(phase)),
  };
};

const flush = () => {
  const { navigation, ...metrics } = pending;
  if (Object.keys(metrics).length === 0) {
    return;
  }
  const body = JSON.stringify({ page: pageGroup(), build: buildId(), navigation, metrics });
  for (const key of Object.keys(pending)) {
    delete pending[key];
  }
  navigator.sendBeacon(endpoint, new Blob([body], { type: "application/json" }));
};

addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    flush();
  }
});
addEventListener("pagehide", flush);

for (const observe of [onCLS, onFCP, onINP, onLCP, onTTFB]) {
  observe(record);
}
