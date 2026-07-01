import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyRuntimeFix,
  inspectRuntime,
  patchPromptRuntimeShutdown,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-runtime-shutdown-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-runtime-shutdown-fix-"));

try {
  const runtimePath = path.join(tempRoot, "runtime.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { join, resolve, dirname } from 'path';
import { existsSync, appendFileSync, mkdirSync, openSync, closeSync } from 'fs';
import { mkdir, readdir, readFile, writeFile } from 'fs/promises';
import { spawn, spawnSync } from 'child_process';
import { resolveCanonicalTeamStateRoot } from './state-root.js';

function isPidAlive(pid) {
    return Number.isFinite(pid) && pid > 0;
}
async function waitForTrackedPidsExit(tracked, timeoutMs) {
    return tracked.every((pid) => !isPidAlive(pid));
}
async function terminateTrackedProcessTree(rootPid, processGroupId = null, graceMs = PROMPT_WORKER_SIGTERM_WAIT_MS, killWaitMs = PROMPT_WORKER_SIGKILL_WAIT_MS) {
    if (process.platform === 'win32') {
        const trackedPids = Number.isFinite(rootPid) && rootPid > 0 ? [rootPid] : [];
        if (trackedPids.length === 0) {
            return { terminated: true, forcedKill: false, trackedPids: [] };
        }
        const taskkill = spawnSync('taskkill', ['/PID', String(rootPid), '/T', '/F'], {
            stdio: 'ignore',
            windowsHide: true,
        });
        if (taskkill.error && taskkill.error.code !== 'ESRCH') {
            process.stderr.write(\`[team/runtime] operation failed: \${taskkill.error}\\n\`);
        }
        return {
            terminated: await waitForTrackedPidsExit(trackedPids, killWaitMs),
            forcedKill: true,
            trackedPids,
        };
    }
    return { terminated: true, forcedKill: false, trackedPids: [] };
}
async function teardownPromptWorker(teamName, workerName, fallbackPid, cwd, context) {
    const handle = getPromptWorkerHandle(teamName, workerName);
    const handlePid = handle?.pid;
    const processGroupId = handle?.processGroupId ?? null;
    const pid = (typeof handlePid === 'number' && Number.isFinite(handlePid))
        ? handlePid
        : (Number.isFinite(fallbackPid) && (fallbackPid ?? 0) > 0 ? fallbackPid : null);
    if (pid === null && processGroupId === null) {
        removePromptWorkerHandle(teamName, workerName);
        return { terminated: true, forcedKill: false, pid: null };
    }
    const teardown = await terminateTrackedProcessTree(pid ?? 0, processGroupId);
    const processGone = processGroupId ? !isProcessGroupAlive(processGroupId) : !isPidAlive(pid);
    if (teardown.terminated && processGone) {
        removePromptWorkerHandle(teamName, workerName);
        return { terminated: true, forcedKill: teardown.forcedKill, pid };
    }
}
`;

  const preview = patchPromptRuntimeShutdown(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /import \{ existsSync, appendFileSync, mkdirSync, openSync, closeSync, readFileSync \} from 'fs';/);
  assert.match(preview.content, /function collectWindowsPromptControllerDiagnosticPids\(teamName, workerName, cwd\)/);
  assert.match(preview.content, /prompt-controller-debug', teamName, `\$\{workerName\}\.child-pid\.json`/);
  assert.match(preview.content, /'team', teamName, 'workers', workerName, 'child-pid\.json'/);
  assert.match(preview.content, /parsed\?\.pids/);
  assert.match(preview.content, /parsed\?\.pid, parsed\?\.child_pid, parsed\?\.active_child_pid/);
  assert.match(preview.content, /return \[\.\.\.new Set\(pids\)\]/);
  assert.match(preview.content, /killWaitMs = PROMPT_WORKER_SIGKILL_WAIT_MS, extraTrackedPids = \[\]/);
  assert.match(preview.content, /for \(const targetPid of trackedPids\)[\s\S]*spawnSync\('taskkill'/);
  assert.match(preview.content, /process\.kill\(targetPid, 'SIGTERM'\)/);
  assert.match(preview.content, /process\.kill\(targetPid, 'SIGKILL'\)/);
  assert.match(preview.content, /collectWindowsPromptControllerDiagnosticPids\(teamName, workerName, cwd\)/);
  assert.match(preview.content, /terminateTrackedProcessTree\(pid \?\? 0, processGroupId, PROMPT_WORKER_SIGTERM_WAIT_MS, PROMPT_WORKER_SIGKILL_WAIT_MS, extraTrackedPids\)/);

  const crlfPreview = patchPromptRuntimeShutdown(original.replace(/\n/g, "\r\n"));
  assert.equal(crlfPreview.changed, true);
  assert.equal(crlfPreview.status, "patched");
  assert.match(crlfPreview.content, new RegExp(PATCH_MARKER));
  assert.match(crlfPreview.content, /terminateTrackedProcessTree\(pid \?\? 0, processGroupId, PROMPT_WORKER_SIGTERM_WAIT_MS, PROMPT_WORKER_SIGKILL_WAIT_MS, extraTrackedPids\)/);

  const already = patchPromptRuntimeShutdown(preview.content);
  assert.equal(already.changed, false);
  assert.equal(already.status, "already_patched");

  assert.equal(patchPromptRuntimeShutdown(original.replace("import { existsSync, appendFileSync, mkdirSync, openSync, closeSync } from 'fs';", "import fs from 'fs';")).status, "fs_import_missing");
  assert.equal(patchPromptRuntimeShutdown(original.replace("async function terminateTrackedProcessTree", "async function terminateTrackedProcessTreeMissing")).status, "terminate_function_missing");
  assert.equal(patchPromptRuntimeShutdown(original.replace("const taskkill = spawnSync('taskkill', ['/PID', String(rootPid), '/T', '/F'], {", "const taskkill = spawnSync('taskkill', ['/PID', String(rootPid)], {")).status, "windows_taskkill_block_missing");
  assert.equal(patchPromptRuntimeShutdown(original.replace("const teardown = await terminateTrackedProcessTree(pid ?? 0, processGroupId);", "const teardown = await terminateTrackedProcessTree(pid ?? 0);" )).status, "teardown_call_missing");

  await fs.writeFile(runtimePath, original, "utf8");
  const applied = await applyRuntimeFix(runtimePath, backupDir);
  assert.equal(applied.ok, true);
  assert.equal(applied.status, "patched");
  assert.equal(applied.changed, true);
  assert.ok(applied.backupPath);

  const inspected = await inspectRuntime(runtimePath, backupDir);
  assert.equal(inspected.ok, true);
  assert.equal(inspected.patched, true);
  assert.equal(inspected.backupCount, 1);

  const secondApply = await applyRuntimeFix(runtimePath, backupDir);
  assert.equal(secondApply.changed, false);
  assert.equal(secondApply.status, "already_patched");

  const restored = await restoreLatestBackup(runtimePath, backupDir);
  assert.equal(restored.ok, true);
  assert.equal(restored.status, "restored");
  assert.equal(await fs.readFile(runtimePath, "utf8"), original);

  console.log("openclaw-omx-windows-prompt-runtime-shutdown-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
