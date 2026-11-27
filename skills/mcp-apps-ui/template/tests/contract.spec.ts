import { expect, test } from "@playwright/test";
import { readServiceStatus } from "../src/contract.ts";
import { invalidFixtures, validFixtures, validateServiceStatus } from "./contract.ts";

for (const [file, fixture] of validFixtures) {
  test(`fixture ${file} satisfies the schema and the view's reader`, () => {
    expect(validateServiceStatus(fixture), JSON.stringify(validateServiceStatus.errors)).toBe(true);
    expect(readServiceStatus(fixture)).not.toBeNull();
  });
}

for (const [file, fixture] of invalidFixtures) {
  test(`invalid fixture ${file} is rejected by the schema`, () => {
    expect(validateServiceStatus(fixture)).toBe(false);
  });
}

test("the view's reader rejects a state outside the contract", () => {
  const unknownState = invalidFixtures.find(([file]) => file === "unknown-state.json")?.[1];
  expect(readServiceStatus(unknownState)).toBeNull();
});
