import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptControllerDebugRoot,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-debug-root-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-debug-root-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { dirname, join } from 'path';
async function main() {
    const workerRef = String(process.env.OMX_TEAM_WORKER ?? '').trim();
    const [teamName = '', workerName = ''] = workerRef.split('/');
    const teamStateRoot = String(process.env.OMX_TEAM_STATE_ROOT ?? '').trim() || join(process.cwd(), '.omx', 'state');
    const inboxPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'inbox.md')
        : '';
    const controllerLogPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'controller.log')
        : '';
    const execStdoutLogPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec.stdout.log')
        : '';
    const execStderrLogPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec.stderr.log')
        : '';
}
`;

  const preview = patchPromptControllerDebugRoot(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /OMX_WINDOWS_PROMPT_CONTROLLER_DEBUG_ROOT/);
  assert.match(preview.content, /workerName}\.controller\.log/);
  assert.match(preview.content, /workerName}\.exec\.stdout\.log/);
  assert.match(preview.content, /workerName}\.exec\.stderr\.log/);

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

  console.log("openclaw-omx-windows-prompt-controller-debug-root-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
