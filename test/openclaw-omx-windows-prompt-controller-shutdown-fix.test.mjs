import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptControllerShutdown,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-shutdown-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-shutdown-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { appendFileSync, closeSync, existsSync, mkdirSync, openSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { spawn } from 'child_process';

async function main() {
    const teamName = 'team-a';
    const workerName = 'worker-1';
    const teamStateRoot = join(process.cwd(), '.omx', 'state');
    const controllerDebugRoot = join(teamStateRoot, 'prompt-controller-debug', teamName);
    const statusPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'status.json')
        : '';
    const omxEntryPath = resolveOmxCliEntryPath();
    const queue = [];
    let activeChild = null;
    const log = (event, details = {}) => {
        if (controllerLogPath === '')
            return;
        try {
            mkdirSync(dirname(controllerLogPath), { recursive: true });
        }
        catch {
            // Fall through to append attempt.
        }
        try {
            appendFileSync(controllerLogPath, \`\${JSON.stringify({ ts: new Date().toISOString(), event, ...details })}\\n\`, 'utf-8');
        }
        catch {
            // Best-effort debug log only.
        }
    };
    function launchExecTurn(promptText) {
        const normalizedPrompt = promptText;
        const launchMode = 'exec_arg';
        const command = 'node';
        const args = ['worker.js'];
        const stdoutFd = execStdoutLogPath !== '' ? openSync(execStdoutLogPath, 'a') : 'ignore';
        const stderrFd = execStderrLogPath !== '' ? openSync(execStderrLogPath, 'a') : 'ignore';
        activeChild = spawn(command, args, {
                cwd: process.cwd(),
                env: process.env,
                stdio: ['pipe', stdoutFd, stderrFd],
                windowsHide: true,
            });
            // OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_STDIN_CLOSE_FIX_V1
        activeChild.once('exit', () => {
            log('exec_exit', { code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null });
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

  const preview = patchPromptControllerShutdown(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /const childPidPath = teamName && workerName && controllerDebugRoot/);
  assert.match(preview.content, /join\(controllerDebugRoot, `\$\{workerName\}\.child-pid\.json`\)/);
  assert.match(preview.content, /join\(teamStateRoot, 'team', teamName, 'workers', workerName, 'child-pid\.json'\)/);
  assert.match(preview.content, /const writeChildPidSnapshot = \(details = \{\}\) =>/);
  assert.match(preview.content, /pid: childPid/);
  assert.match(preview.content, /child_pid: childPid/);
  assert.match(preview.content, /active: activeChild !== null && activeChild\.exitCode === null/);
  assert.match(preview.content, /const terminateActiveChild = \(reason\) =>/);
  assert.match(preview.content, /if \(child === null \|\| child\.exitCode !== null\)\s+return;/);
  assert.match(preview.content, /child\.kill\('SIGTERM'\)/);
  assert.match(preview.content, /child\.kill\('SIGKILL'\)/);
  assert.match(preview.content, /setTimeout\(\(\) => \{[\s\S]*\}, 1000\)\.unref\?\.\(\);/);
  assert.match(preview.content, /const requestControllerShutdown = \(signal\) =>/);
  assert.match(preview.content, /process\.once\('SIGTERM', \(\) => requestControllerShutdown\('SIGTERM'\)\)/);
  assert.match(preview.content, /process\.once\('SIGINT', \(\) => requestControllerShutdown\('SIGINT'\)\)/);
  assert.match(preview.content, /setTimeout\(\(\) => process\.exit\(0\), 1500\)\.unref\?\.\(\);/);
  assert.match(preview.content, /writeChildPidSnapshot\(\{ event: 'launch_exec', launchMode, promptLength: normalizedPrompt\.length \}\)/);
  assert.match(preview.content, /writeChildPidSnapshot\(\{ event: 'exec_exit', code: activeChild\?\.exitCode \?\? null, signal: activeChild\?\.signalCode \?\? null, active: false \}\)/);

  const crlfPreview = patchPromptControllerShutdown(original.replace(/\n/g, "\r\n"));
  assert.equal(crlfPreview.changed, true);
  assert.equal(crlfPreview.status, "patched");
  assert.match(crlfPreview.content, new RegExp(PATCH_MARKER));
  assert.match(crlfPreview.content, /writeChildPidSnapshot\(\{ event: 'launch_exec', launchMode, promptLength: normalizedPrompt\.length \}\)/);

  const already = patchPromptControllerShutdown(preview.content);
  assert.equal(already.changed, false);
  assert.equal(already.status, "already_patched");

  assert.equal(patchPromptControllerShutdown(original.replace("const statusPath = teamName && workerName && teamStateRoot", "const statusPathMissing = teamName && workerName && teamStateRoot")).status, "status_path_block_missing");
  assert.equal(patchPromptControllerShutdown(original.replace("const log = (event, details = {}) => {", "const logMissing = (event, details = {}) => {")).status, "log_block_missing");
  assert.equal(patchPromptControllerShutdown(original.replace("activeChild = spawn(command, args, {", "activeChild = spawn(command, args.filter(Boolean), {")).status, "spawn_block_missing");
  assert.equal(patchPromptControllerShutdown(original.replace("activeChild.once('exit', () => {", "activeChild.once('close', () => {")).status, "exit_block_missing");

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

  console.log("openclaw-omx-windows-prompt-controller-shutdown-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
