import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applyBootstrapFix,
  inspectBootstrap,
  patchWorkerBootstrapMailboxExamples,
  restoreLatestBackup,
} from "../tools/openclaw-omx-windows-worker-bootstrap-mailbox-example-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-worker-bootstrap-mailbox-example-fix-"));

try {
  const bootstrapPath = path.join(tempRoot, "worker-bootstrap.js");
  const backupDir = path.join(tempRoot, "backups");
  const original = [
    "## Startup Handshake (Required)",
    "Before doing any task work, send exactly one startup ACK to the leader.",
    "Keep the body short and deterministic so all worker CLIs (Codex/Claude) behave consistently.",
    "",
    "Example:",
    'omx team api send-message --input "{\\"team_name\\":\\"${teamName}\\",\\"from_worker\\":\\"<your-worker-name>\\",\\"to_worker\\":\\"leader-fixed\\",\\"body\\":\\"ACK: <your-worker-name> initialized\\"}" --json',
    "",
    "CRITICAL: Never omit from_worker. The MCP server cannot auto-detect your identity.",
    "",
    "When your mailbox receives a message, process delivery explicitly:",
    '1. Read: \\`omx team api mailbox-list --input "{\\"team_name\\":\\"${teamName}\\",\\"worker\\":\\"<your-worker-name>\\"}" --json\\`',
    '2. Mark delivered: \\`omx team api mailbox-mark-delivered --input "{\\"team_name\\":\\"${teamName}\\",\\"worker\\":\\"<your-worker-name>\\",\\"message_id\\":\\"<MESSAGE_ID>\\"}" --json\\`',
    "3. If you reply, include concrete progress and keep executing your assigned work or the next feasible task after replying.",
    "",
  ].join("\n");

  const preview = patchWorkerBootstrapMailboxExamples(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /ConvertTo-Json -Compress/);
  assert.match(preview.content, /mailbox-list --input \$payload --json/);
  assert.match(preview.content, /mailbox-mark-delivered --input \$payload --json/);
  assert.doesNotMatch(preview.content, /mailbox-list --input "\{/);

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

  console.log("openclaw-omx-windows-worker-bootstrap-mailbox-example-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
