import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyBootstrapFix,
  inspectBootstrap,
  patchWorkerBootstrapOneliners,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-worker-bootstrap-oneliner-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-worker-bootstrap-oneliner-fix-"));

try {
  const bootstrapPath = path.join(tempRoot, "worker-bootstrap.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = `
function buildSendMessageExample(teamName, workerName) {
    if (process.platform === 'win32') {
        return \`$payload = @{ team_name = "\${teamName}"; from_worker = "\${workerName}"; to_worker = "leader-fixed"; body = "ACK: \${workerName} initialized" } | ConvertTo-Json -Compress\\nomx team api send-message --input $payload --json\`;
    }
}
function buildMailboxListExample(teamName, workerName) {
    if (process.platform === 'win32') {
        return \`$payload = @{ team_name = "\${teamName}"; worker = "\${workerName}" } | ConvertTo-Json -Compress\\nomx team api mailbox-list --input $payload --json\`;
    }
}
function buildMailboxDeliveredExample(teamName, workerName) {
    if (process.platform === 'win32') {
        return \`$payload = @{ team_name = "\${teamName}"; worker = "\${workerName}"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress\\nomx team api mailbox-mark-delivered --input $payload --json\`;
    }
}
`;

  const preview = patchWorkerBootstrapOneliners(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /send-message --input \(@\{ team_name = "\$\{teamName\}"/);
  assert.match(preview.content, /mailbox-list --input \(@\{ team_name = "\$\{teamName\}"/);
  assert.match(preview.content, /mailbox-mark-delivered --input \(@\{ team_name = "\$\{teamName\}"/);
  assert.doesNotMatch(preview.content, /\$payload = @/);

  await fs.writeFile(bootstrapPath, original, "utf8");
  const applied = await applyBootstrapFix(bootstrapPath, backupDir);
  assert.equal(applied.ok, true);
  assert.equal(applied.status, "patched");
  assert.equal(applied.changed, true);
  assert.ok(applied.backupPath);

  const inspected = await inspectBootstrap(bootstrapPath, backupDir);
  assert.equal(inspected.ok, true);
  assert.equal(inspected.patched, true);
  assert.equal(inspected.backupCount, 1);

  const secondApply = await applyBootstrapFix(bootstrapPath, backupDir);
  assert.equal(secondApply.changed, false);
  assert.equal(secondApply.status, "already_patched");

  const restored = await restoreLatestBackup(bootstrapPath, backupDir);
  assert.equal(restored.ok, true);
  assert.equal(restored.status, "restored");
  assert.equal(await fs.readFile(bootstrapPath, "utf8"), original);

  console.log("openclaw-omx-windows-worker-bootstrap-oneliner-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
