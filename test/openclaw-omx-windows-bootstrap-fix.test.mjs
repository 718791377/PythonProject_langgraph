import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyRuntimeFix,
  inspectRuntime,
  patchWindowsPromptBootstrap,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-bootstrap-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-bootstrap-fix-"));

try {
  const runtimePath = path.join(tempRoot, "runtime.js");
  const legacyRuntimePath = path.join(tempRoot, "runtime-legacy.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
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
        const bootstrapScript = [
            "$ErrorActionPreference = 'Stop'",
            \`$p = Start-Process -FilePath \${quotePowerShellArg(process.execPath)} \`
                + \`-ArgumentList @(\${quotePowerShellArg(controllerPath)}) \`
                + \`-WorkingDirectory \${quotePowerShellArg(workerCwd)} \`
                + "-WindowStyle Hidden -PassThru",
            "[Console]::Out.Write($p.Id)",
        ].join('; ');
        const bootstrap = spawnSync('powershell.exe', [
            '-NoLogo',
            '-NoProfile',
            '-NonInteractive',
            '-ExecutionPolicy',
            'Bypass',
            '-EncodedCommand',
            encodePowerShellCommand(bootstrapScript),
        ], {
            cwd: workerCwd,
            env: launchEnv,
            encoding: 'utf-8',
            stdio: ['ignore', 'pipe', 'pipe'],
            windowsHide: true,
        });
        if (bootstrap.error) {
            throw bootstrap.error;
        }
        if (bootstrap.status !== 0) {
            const detail = (bootstrap.stderr || bootstrap.stdout || '').trim();
            throw new Error(detail || \`windows_prompt_controller_bootstrap_failed:\${bootstrap.status}\`);
        }
        const controllerPid = Number.parseInt((bootstrap.stdout || '').trim(), 10);
        if (!Number.isFinite(controllerPid) || controllerPid <= 0) {
            throw new Error('windows_prompt_controller_bootstrap_missing_pid');
        }
        registerPromptWorkerHandle(teamName, workerName, null, controllerPid);
        return { child: null, pid: controllerPid };
    }
}
`;

  const patchPreview = patchWindowsPromptBootstrap(original);
  assert.equal(patchPreview.changed, true);
  assert.equal(patchPreview.status, "patched");
  assert.match(patchPreview.content, new RegExp(PATCH_MARKER));
  assert.doesNotMatch(patchPreview.content, /spawnSync\('powershell\.exe'/);
  assert.match(patchPreview.content, /const controllerChild = spawn\(process\.execPath, \[controllerPath\]/);
  assert.match(patchPreview.content, /controllerChild\.unref\(\)/);

  const legacyPatched = original.replace(
    /const bootstrapScript = \[[\s\S]*?registerPromptWorkerHandle\(teamName, workerName, null, controllerPid\);\s*return \{ child: null, pid: controllerPid \};/m,
    [
      "        const controllerChild = spawn(process.execPath, [controllerPath], {",
      "            cwd: workerCwd,",
      "            env: launchEnv,",
      "            stdio: 'ignore',",
      "            windowsHide: true,",
      "        });",
      "        if (controllerChild.error) {",
      "            throw controllerChild.error;",
      "        }",
      "        const controllerPid = controllerChild.pid ?? 0;",
      "        if (!Number.isFinite(controllerPid) || controllerPid <= 0) {",
      "            throw new Error('windows_prompt_controller_bootstrap_missing_pid');",
      "        }",
      "        controllerChild.unref();",
      "        registerPromptWorkerHandle(teamName, workerName, null, controllerPid);",
      "        return { child: null, pid: controllerPid };",
    ].join("\n"),
  );
  const normalizedLegacy = patchWindowsPromptBootstrap(legacyPatched);
  assert.equal(normalizedLegacy.changed, true);
  assert.equal(normalizedLegacy.status, "normalized_legacy_patch");
  assert.match(normalizedLegacy.content, new RegExp(PATCH_MARKER));

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

  await fs.writeFile(legacyRuntimePath, legacyPatched, "utf8");
  const normalizedApplied = await applyRuntimeFix(legacyRuntimePath, backupDir);
  assert.equal(normalizedApplied.ok, true);
  assert.equal(normalizedApplied.status, "normalized_legacy_patch");
  const legacyInspection = await inspectRuntime(legacyRuntimePath, backupDir);
  assert.equal(legacyInspection.patched, true);

  const restored = await restoreLatestBackup(runtimePath, backupDir);
  assert.equal(restored.ok, true);
  assert.equal(restored.status, "restored");
  assert.equal(await fs.readFile(runtimePath, "utf8"), original);

  console.log("openclaw-omx-windows-bootstrap-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
