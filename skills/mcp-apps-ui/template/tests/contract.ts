import { readFileSync, readdirSync } from "node:fs";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import schema from "../contract/service-status.schema.json" with { type: "json" };

const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);

export const validateServiceStatus = ajv.compile(schema);

function readJsonDir(dir: string): Array<[string, unknown]> {
  const url = new URL(`../contract/${dir}/`, import.meta.url);
  return readdirSync(url)
    .filter((file) => file.endsWith(".json"))
    .map((file) => [file, JSON.parse(readFileSync(new URL(file, url), "utf8"))]);
}

export const validFixtures = readJsonDir("fixtures");
export const invalidFixtures = readJsonDir("invalid");

export function compileSchema(candidate: object) {
  return new Ajv2020({ strict: false }).addFormat("date-time", true).compile(candidate);
}
