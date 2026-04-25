import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptControllerStdinClose,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-stdin-close-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-stdin-close-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
function launchExecTurn(promptText) {
    const stdoutFd = execStdoutLogPath !== '' ? openSync(execStdoutLogPath, 'a') : 'ignore';
    const stderrFd = execStderrLogPath !== '' ? openSync(execStderrLogPath, 'a') : 'ignore';
    try {
        activeChild = spawn(command, args, {
            cwd: process.cwd(),
            env: process.env,
            stdio: ['ignore', stdoutFd, stderrFd],
            windowsHide: true,
        });
    }
    catch (error) {
        log('spawn_throw', {
            command,
            args,
            message: error instanceof Error ? error.message : String(error),
        });
    }
}
`;

  const preview = patchPromptControllerStdinClose(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /stdio: \['pipe', stdoutFd, stderrFd\]/);
  assert.match(preview.content, /activeChild\.stdin\?\.end\(\)/);
  assert.match(preview.content, /stdin_close_error/);

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

  console.log("openclaw-omx-windows-prompt-controller-stdin-close-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
