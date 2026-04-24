import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  PATCH_MARKER,
  applySkillFix,
  inspectSkill,
  patchWorkerSkillPowerShellOneliners,
  restoreLatestBackup,
} from "../tools/openclaw-omx-worker-skill-powershell-oneliner-fix.mjs";

const TEST_ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".tmp");
await fs.mkdir(TEST_ROOT, { recursive: true });
const tempRoot = await fs.mkdtemp(path.join(TEST_ROOT, "openclaw-omx-worker-skill-powershell-oneliner-fix-"));

try {
  const skillPath = path.join(tempRoot, "SKILL.md");
  const backupDir = path.join(tempRoot, "backups");
  const original = [
    "Windows PowerShell:",
    "",
    "```powershell",
    "$payload = @{",
    '  team_name = "<teamName>"',
    '  from_worker = "<workerName>"',
    '  to_worker = "leader-fixed"',
    '  body = "ACK: <workerName> initialized"',
    "} | ConvertTo-Json -Compress",
    "omx team api send-message --input $payload --json",
    "```",
    "",
    "Windows PowerShell:",
    "",
    "```powershell",
    "$payload = @{",
    '  team_name = "<teamName>"',
    '  worker = "<workerName>"',
    "} | ConvertTo-Json -Compress",
    "omx team api mailbox-list --input $payload --json",
    "",
    "$payload = @{",
    '  team_name = "<teamName>"',
    '  worker = "<workerName>"',
    '  message_id = "<MESSAGE_ID>"',
    "} | ConvertTo-Json -Compress",
    "omx team api mailbox-mark-delivered --input $payload --json",
    "```",
    "",
  ].join("\n");

  const preview = patchWorkerSkillPowerShellOneliners(original);
  assert.equal(preview.changed, true);
  assert.equal(preview.status, "patched");
  assert.match(preview.content, new RegExp(PATCH_MARKER));
  assert.match(preview.content, /send-message --input \(@\{/);
  assert.match(preview.content, /mailbox-list --input \(@\{/);
  assert.doesNotMatch(preview.content, /\$payload = @\{/);

  await fs.writeFile(skillPath, original, "utf8");
  const applied = await applySkillFix(skillPath, backupDir);
  assert.equal(applied.ok, true);
  assert.equal(applied.status, "patched");
  assert.equal(applied.changed, true);
  assert.ok(applied.backupPath);

  const inspected = await inspectSkill(skillPath, backupDir);
  assert.equal(inspected.ok, true);
  assert.equal(inspected.patched, true);
  assert.equal(inspected.backupCount, 1);

  const secondApply = await applySkillFix(skillPath, backupDir);
  assert.equal(secondApply.changed, false);
  assert.equal(secondApply.status, "already_patched");

  const restored = await restoreLatestBackup(skillPath, backupDir);
  assert.equal(restored.ok, true);
  assert.equal(restored.status, "restored");
  assert.equal(await fs.readFile(skillPath, "utf8"), original);

  console.log("openclaw-omx-worker-skill-powershell-oneliner-fix: ok");
} finally {
  await fs.rm(tempRoot, { recursive: true, force: true });
}
