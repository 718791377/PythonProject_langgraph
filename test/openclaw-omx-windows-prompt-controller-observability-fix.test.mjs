import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyRuntimeFix,
  inspectRuntime,
  patchPromptControllerObservability,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-observability-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-observability-fix-"));

try {
  const runtimePath = path.join(tempRoot, "runtime.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { join, resolve, dirname } from 'path';
import { existsSync, appendFileSync, mkdirSync } from 'fs';
function spawnPromptWorker(teamName, workerName, workerIndex, workerCwd, launchArgs, workerEnv, workerCli, initialPrompt, workerRole) {
    const processSpec = buildWorkerProcessLaunchSpec(teamName, workerIndex, launchArgs, workerCwd, workerEnv, workerCli, initialPrompt, workerRole);
    if (isNativeWindows() && workerCli === 'codex') {
        const omxEntryPath = resolveOmxCliEntryPath();
        if (!omxEntryPath) {
            throw new Error('windows_prompt_controller_missing_omx_entry');
        }
        const controllerPath = join(dirname(omxEntryPath), '..', 'team', 'windows-worker-controller.js');
        const launchEnv = {
            ...process.env,
            ...processSpec.env,
            ...workerEnv,
            [TEAM_WORKER_ENV]: \`\${teamName}/\${workerName}\`,
            OMX_WINDOWS_PROMPT_WORKER_LAUNCH_ARGS_JSON: JSON.stringify(launchArgs),
            OMX_WINDOWS_PROMPT_WORKER_INITIAL_PROMPT: initialPrompt ?? '',
            OMX_WINDOWS_PROMPT_WORKER_ROLE: workerRole ?? '',
        };
        const controllerChild = spawn(process.execPath, [controllerPath], {
            cwd: workerCwd,
            env: launchEnv,
            stdio: 'ignore',
            windowsHide: true,
        });
        if (controllerChild.error) {
            throw controllerChild.error;
        }
        const controllerPid = controllerChild.pid ?? 0;
        if (!Number.isFinite(controllerPid) || controllerPid <= 0) {
            throw new Error('windows_prompt_controller_bootstrap_missing_pid');
        }
        controllerChild.unref();
        registerPromptWorkerHandle(teamName, workerName, null, controllerPid);
        return { child: null, pid: controllerPid };
    }
}
`;

  const preview = patchPromptControllerObservability(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /openSync, closeSync/);
  assert.match(preview.content, /resolveCanonicalTeamStateRoot\(workerCwd, \{ \.\.\.process\.env, \.\.\.processSpec\.env, \.\.\.workerEnv \}\)/);
  assert.match(preview.content, /const controllerDebugRoot = join\(teamStateRoot, 'prompt-controller-debug', teamName\);/);
  assert.match(preview.content, /OMX_WINDOWS_PROMPT_CONTROLLER_DEBUG_ROOT: controllerDebugRoot/);
  assert.match(preview.content, /controllerStdoutLogPath/);
  assert.match(preview.content, /controllerStderrLogPath/);
  assert.match(preview.content, /controller_bootstrap_spawned/);
  assert.match(preview.content, /controller_bootstrap_exit/);
  assert.match(preview.content, /registerPromptWorkerHandle\(teamName, workerName, controllerChild, controllerPid\)/);

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

  const legacyPatched = preview.content.replace(/prompt-controller-debug/g, "team");
  const normalized = patchPromptControllerObservability(legacyPatched);
  assert.equal(normalized.changed, true);
  assert.equal(normalized.status, "normalized_legacy_patch");
  assert.match(normalized.content, /prompt-controller-debug/);

  const restored = await restoreLatestBackup(runtimePath, backupDir);
  assert.equal(restored.ok, true);
  assert.equal(restored.status, "restored");
  assert.equal(await fs.readFile(runtimePath, "utf8"), original);

  console.log("openclaw-omx-windows-prompt-controller-observability-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
