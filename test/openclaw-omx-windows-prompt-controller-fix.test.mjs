import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptController,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { dirname, join } from 'path';
async function main() {
    const omxEntryPath = resolveOmxCliEntryPath();
    if (!omxEntryPath) {
        throw new Error('windows_prompt_controller_missing_omx_entry');
    }
    const teamStateRoot = String(process.env.OMX_TEAM_STATE_ROOT ?? '').trim();
    const leaderCliPath = String(process.env.OMX_LEADER_CLI_PATH ?? '').trim();
    const leaderNodePath = String(process.env.OMX_LEADER_NODE_PATH ?? process.execPath).trim() || process.execPath;
    const syntheticTrigger = inboxPath
        ? \`Read \${inboxPath}, start work now\`
        : '';
    const launchMode = leaderCliPath.toLowerCase().endsWith('.js') ? 'codex_exec_direct_js' : 'omx_exec_fallback';
}
`;

  const preview = patchPromptController(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /const teamStateRoot = String\(process\.env\.OMX_TEAM_STATE_ROOT \?\? ''\)\.trim\(\) \|\| join\(process\.cwd\(\), '\.omx', 'state'\);/);
  assert.match(preview.content, /const derivedLeaderCliPath = join\(dirname\(omxEntryPath\), 'index\.js'\);/);
  assert.match(preview.content, /leaderCliPathRaw\.toLowerCase\(\)\.endsWith\('\.js'\)/);

  await fs.writeFile(controllerPath, original, "utf8");
  const applied = await applyControllerFix(controllerPath, backupDir);
  assert.equal(applied.ok, true);
  assert.equal(applied.status, "patched");
  assert.equal(applied.changed, true);
  assert.ok(applied.backupPath);

  const inspected = await inspectController(controllerPath, backupDir);
  assert.equal(inspected.ok, true);
  assert.equal(inspected.patched, true);
  assert.equal(inspected.backupCount, 1);

  const secondApply = await applyControllerFix(controllerPath, backupDir);
  assert.equal(secondApply.changed, false);
  assert.equal(secondApply.status, "already_patched");

  const restored = await restoreLatestBackup(controllerPath, backupDir);
  assert.equal(restored.ok, true);
  assert.equal(restored.status, "restored");
  assert.equal(await fs.readFile(controllerPath, "utf8"), original);

  console.log("openclaw-omx-windows-prompt-controller-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
