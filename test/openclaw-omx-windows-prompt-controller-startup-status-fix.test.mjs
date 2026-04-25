import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyControllerFix,
  inspectController,
  patchPromptControllerStartupStatus,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-controller-startup-status-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-controller-startup-status-fix-"));

try {
  const controllerPath = path.join(tempRoot, "windows-worker-controller.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
import { appendFileSync, closeSync, existsSync, mkdirSync, openSync, readFileSync } from 'fs';
import { dirname, join } from 'path';
async function main() {
    const workerRef = String(process.env.OMX_TEAM_WORKER ?? '').trim();
    const [teamName = '', workerName = ''] = workerRef.split('/');
    const teamStateRoot = String(process.env.OMX_TEAM_STATE_ROOT ?? '').trim() || join(process.cwd(), '.omx', 'state');
    const execStderrLogPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec.stderr.log')
        : '';
    let firstTaskClaimed = false;
    const log = (event, details = {}) => {};
    const maybeClaimFirstTask = async () => {
        if (firstTaskClaimed || teamName === '' || workerName === '')
            return;
        const tasks = await teamListTasks(teamName, process.cwd());
        const candidate = tasks.find((task) => task.owner === workerName && task.status === 'pending');
        if (!candidate)
            return;
        const result = await executeTeamApiOperation('claim-task', {
            team_name: teamName,
            task_id: candidate.id,
            worker: workerName,
            expected_version: candidate.version,
        }, process.cwd());
        log('claim_task', { ok: result.ok, taskId: candidate.id });
        if (result.ok) {
            firstTaskClaimed = true;
        }
    };
}
`;

  const preview = patchPromptControllerStartupStatus(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /writeFileSync/);
  assert.match(preview.content, /const statusPath = teamName && workerName && teamStateRoot/);
  assert.match(preview.content, /current_task_id: candidate.id/);
  assert.match(preview.content, /status_seed_error/);

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

  console.log("openclaw-omx-windows-prompt-controller-startup-status-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
