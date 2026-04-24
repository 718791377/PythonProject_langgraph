import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyRuntimeFix,
  inspectRuntime,
  patchPromptStartupEvidence,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-prompt-startup-evidence-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-prompt-startup-evidence-fix-"));

try {
  const runtimePath = path.join(tempRoot, "runtime.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
async function dispatchCriticalInboxInstruction(params) {
    const { teamName, config, workerName, workerIndex, paneId, workerCli, inbox, triggerMessage, intent, cwd, dispatchPolicy, inboxCorrelationKey, requireWorkerStartupEvidence, startupEvidenceTimeoutMs, } = params;
    if (config.worker_launch_mode === 'prompt') {
        return await queueInboxInstruction({
            teamName,
            workerName,
            workerIndex,
            paneId,
            inbox,
            triggerMessage,
            intent,
            cwd,
            transportPreference: 'prompt_stdin',
            fallbackAllowed: false,
            inboxCorrelationKey,
            notify: (_target, message) => notifyWorkerOutcome(config, workerIndex, message, paneId),
        });
    }
}
`;

  const preview = patchPromptStartupEvidence(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /const queued = await queueInboxInstruction/);
  assert.match(preview.content, /waitForRequiredStartupEvidenceAfterDirectFallback/);
  assert.match(preview.content, /startup_no_evidence_after_prompt/);
  assert.match(preview.content, /prompt_confirmed:/);

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

  console.log("openclaw-omx-windows-prompt-startup-evidence-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
