import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const repoRoot = process.cwd();
const testRoot = join(repoRoot, "test");
const manifestPath = process.argv[2] ?? join(repoRoot, "tools", "ci", "ci_test_manifest.json");
const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
const testFiles = (manifest.node_mjs ?? [])
  .map((name) => join(testRoot, name))
  .sort();

for (const file of testFiles) {
  if (!existsSync(file)) {
    console.error(`Missing Node.js test file: ${file}`);
    process.exit(1);
  }
}

for (const file of testFiles) {
  await import(pathToFileURL(file).href);
}

console.log(`node_mjs_tests: ok (${testFiles.length} files)`);
