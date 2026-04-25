import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptControllerStdinPrompt,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-stdin-prompt-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-stdin-prompt-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
function launchExecTurn(promptText) {
    const args = launchMode === 'codex_exec_direct_js'
        ? [leaderCliPath, 'exec', '--ephemeral', ...baseLaunchArgs, normalizedPrompt]
        : [omxEntryPath, 'exec', '--ephemeral', ...baseLaunchArgs, normalizedPrompt];
    try {
        activeChild = spawn(command, args, {
            cwd: process.cwd(),
            env: process.env,
            stdio: ['pipe', stdoutFd, stderrFd],
            windowsHide: true,
        });
        try {
            activeChild.stdin?.end();
        }
        catch (error) {
            log('stdin_close_error', {
                message: error instanceof Error ? error.message : String(error),
                launchMode,
            });
        }
    }
    catch (error) {
        log('spawn_throw', { message: String(error) });
    }
}
`;

  const preview = patchPromptControllerStdinPrompt(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /\[leaderCliPath, 'exec', '--ephemeral', \.\.\.baseLaunchArgs, '-'\]/);
  assert.match(preview.content, /activeChild\.stdin\?\.write\(`\$\{normalizedPrompt\}\\n`\)/);
  assert.match(preview.content, /activeChild\.stdin\?\.end\(\)/);

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

  console.log("openclaw-omx-windows-prompt-controller-stdin-prompt-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
