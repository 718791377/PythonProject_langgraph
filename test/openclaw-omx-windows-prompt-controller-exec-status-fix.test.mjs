import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptControllerExecStatus,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-exec-status-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-exec-status-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { appendFileSync, closeSync, existsSync, mkdirSync, openSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';

async function main() {
    const statusPath = join(process.cwd(), 'status.json');
    const childPidPath = join(process.cwd(), 'child-pid.json');
    let activeChild = null;
    const queue = [];
    const log = (event, details = {}) => {};
    const writeChildPidSnapshot = (details = {}) => {
        if (childPidPath === '')
            return;
        const childPid = activeChild?.pid ?? null;
        try {
            mkdirSync(dirname(childPidPath), { recursive: true });
            writeFileSync(childPidPath, JSON.stringify({
                pid: childPid,
                child_pid: childPid,
                active: activeChild !== null && activeChild.exitCode === null,
                updated_at: new Date().toISOString(),
                ...details,
            }, null, 2), 'utf-8');
        }
        catch (error) {
            log('child_pid_snapshot_error', {
                message: error instanceof Error ? error.message : String(error),
            });
        }
    };
    function attachExit() {
        activeChild.once('exit', () => {
            log('exec_exit', { code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null });
            writeChildPidSnapshot({ event: 'exec_exit', code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null, active: false });
            activeChild = null;
            if (queue.length > 0) {
                const next = queue.shift();
                launchExecTurn(next);
                return;
            }
        });
    }
}
`;

  const preview = patchPromptControllerExecStatus(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /const readCurrentTaskIdFromStatus = \(\) =>/);
  assert.match(preview.content, /JSON\.parse\(readFileSync\(statusPath, 'utf-8'\)\)/);
  assert.match(preview.content, /const writeExecFailureStatus = \(code, signal\) =>/);
  assert.match(preview.content, /state: 'failed'/);
  assert.match(preview.content, /failure_reason: normalizedCode !== null \? `child_exec_exit:\$\{normalizedCode\}` : `child_exec_signal:\$\{normalizedSignal\}`/);
  assert.match(preview.content, /const exitCode = activeChild\?\.exitCode \?\? null;/);
  assert.match(preview.content, /const signalCode = activeChild\?\.signalCode \?\? null;/);
  assert.match(preview.content, /writeExecFailureStatus\(exitCode, signalCode\)/);

  const crlfPreview = patchPromptControllerExecStatus(original.replace(/\n/g, "\r\n"));
  assert.equal(crlfPreview.changed, true);
  assert.equal(crlfPreview.status, "patched");
  assert.match(crlfPreview.content, new RegExp(PATCH_MARKER));

  const already = patchPromptControllerExecStatus(preview.content);
  assert.equal(already.changed, false);
  assert.equal(already.status, "already_patched");

  assert.equal(patchPromptControllerExecStatus(original.replace("const writeChildPidSnapshot = (details = {}) => {", "const writeChildPidSnapshotMissing = (details = {}) => {")).status, "child_pid_helper_missing");
  assert.equal(patchPromptControllerExecStatus(original.replace("activeChild.once('exit', () => {", "activeChild.once('close', () => {")).status, "exec_exit_block_missing");

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

  console.log("openclaw-omx-windows-prompt-controller-exec-status-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
