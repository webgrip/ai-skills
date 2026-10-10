# Prove a preset refactor changes no behaviour

A reviewer reading the diff can only argue that a reordered or reworded preset behaves the same.
Renovate's own rule engine can show it: resolve the old and the new preset, push the same synthetic
dependencies through every rule stack consumers use, and diff the outcomes.

1. Install the exact Renovate version the bot runs into a scratch directory
   (`npm install --prefix <scratch>/tool renovate@<version>`). The two imports below are internal
   paths, so they hold for that version only.
2. Save the old preset (from the base branch) and the new one as JSON or JSON5 files.
3. Save the script below as `<scratch>/tool/compare-presets.mjs`. Extend the synthetic lists until
   they cover every `match*` value your rules use: managers, datasources, update types, package
   names and file paths.
4. Run it once per consumer that adds its own rules:
   `LOG_LEVEL=fatal node compare-presets.mjs old.json new.json consumer-renovate.json`.
5. Zero differences is the evidence for the PR. Any difference names the stack, manager, datasource,
   update type and package that changed; read those before deciding the change is intended.
6. Mutate one rule on purpose (an extra `automerge: true`) and confirm the script reports
   differences, so a zero means something.

```js
import { readFileSync } from "node:fs";
import JSON5 from "json5";
import { resolveConfigPresets } from "renovate/dist/config/presets/index.js";
import { applyPackageRules } from "renovate/dist/util/package-rules/index.js";

const [oldPath, newPath, ...localRulePaths] = process.argv.slice(2);
const read = (path) => JSON5.parse(readFileSync(path, "utf8"));
const resolve = async (config) => (await resolveConfigPresets(config)).config;
const localRules = localRulePaths.flatMap((path) => read(path).packageRules ?? []);

const stacks = {
  "preset alone": (preset) => preset,
  "with config:recommended": (preset) => ({ ...preset, extends: ["config:recommended", ...(preset.extends ?? [])] }),
  "with a consumer's own rules": (preset) => ({ ...preset, packageRules: [...(preset.packageRules ?? []), ...localRules] }),
};
const deps = [];
for (const manager of ["dockerfile", "helm-values", "flux", "regex", "npm", "github-actions"])
  for (const datasource of ["docker", "helm", "npm", "github-tags"])
    for (const updateType of ["major", "minor", "patch", "pin", "digest", "pinDigest", "bump", "rollback", "replacement", "lockFileMaintenance"])
      for (const [depName, packageFile] of [["grafana/grafana", "deploy/grafana.yaml"], ["ghcr.io/owner/app", "deploy/app/values.yaml"], ["actions/checkout", ".github/workflows/ci.yml"], ["lodash", "package.json"]])
        deps.push({ manager, datasource, updateType, depName, packageName: depName, packageFile });

const outcome = async (config, dep) => {
  const { description, packageRules, ...rest } = await applyPackageRules({ ...config, ...dep });
  return JSON.stringify(rest, Object.keys(rest).sort());
};

let differences = 0;
for (const [stackName, stack] of Object.entries(stacks)) {
  const before = await resolve(stack(read(oldPath)));
  const after = await resolve(stack(read(newPath)));
  for (const dep of deps) {
    if ((await outcome(before, dep)) !== (await outcome(after, dep))) {
      differences += 1;
      if (differences <= 20) console.log(`${stackName}: ${dep.manager} ${dep.datasource} ${dep.updateType} ${dep.depName}`);
    }
  }
}
console.log(`${deps.length} synthetic dependencies x ${Object.keys(stacks).length} rule stacks: ${differences} differences`);
process.exit(differences ? 1 : 0);
```

`description` is left out of the comparison because rewording it is the usual point of such a
refactor. A preset that extends `local>` or forge presets needs those resolvable from the scratch
directory; inline them into the two files when they are not.
