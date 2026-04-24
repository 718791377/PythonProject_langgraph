import assert from "node:assert/strict";
import {
  PATCH_MARKER,
  patchWorkerBootstrap,
  patchWorkerSkill,
} from "../tools/openclaw-omx-worker-visible-raw-abstraction-fix.mjs";

const workerBootstrapSample = [
  'function buildSendMessageExample(teamName, workerName) {',
  "    if (process.platform === 'win32') {",
  '        return `omx-team-send-message.ps1 -TeamName "${teamName}" -FromWorker "${workerName}" -ToWorker "leader-fixed" -Body "ACK: ${workerName} initialized" -Json`;',
  "    }",
  '    return `omx team api send-message --input "{\\\\"team_name\\\\":\\\\"${teamName}\\\\",\\\\"from_worker\\\\":\\\\"${workerName}\\\\",\\\\"to_worker\\\\":\\\\"leader-fixed\\\\",\\\\"body\\\\":\\\\"ACK: ${workerName} initialized\\\\"}" --json`;',
  "}",
  'function buildMailboxListExample(teamName, workerName) {',
  "    if (process.platform === 'win32') {",
  '        return `omx-team-mailbox-list.ps1 -TeamName "${teamName}" -Worker "${workerName}" -Json`;',
  "    }",
  '    return `omx team api mailbox-list --input "{\\\\"team_name\\\\":\\\\"${teamName}\\\\",\\\\"worker\\\\":\\\\"${workerName}\\\\"}" --json`;',
  "}",
  'function buildMailboxDeliveredExample(teamName, workerName) {',
  "    if (process.platform === 'win32') {",
  '        return `omx-team-mailbox-mark-delivered.ps1 -TeamName "${teamName}" -Worker "${workerName}" -MessageId "<MESSAGE_ID>" -Json`;',
  "    }",
  '    return `omx team api mailbox-mark-delivered --input "{\\\\"team_name\\\\":\\\\"${teamName}\\\\",\\\\"worker\\\\":\\\\"${workerName}\\\\",\\\\"message_id\\\\":\\\\"<MESSAGE_ID>\\\\"}" --json`;',
  "}",
  "function buildWorkerRootAgentsBackupPath(teamStateRoot, teamName, workerName, worktreePath) {",
  "}",
  "Example:\n// OPENCLAW_OMX_WINDOWS_WORKER_BOOTSTRAP_MAILBOX_EXAMPLE_FIX_V1\n$payload = @{ team_name = \"${teamName}\"; from_worker = \"<your-worker-name>\"; to_worker = \"leader-fixed\"; body = \"ACK: <your-worker-name> initialized\" } | ConvertTo-Json -Compress\nomx team api send-message --input $payload --json",
  "1. Read:\n   \\`$payload = @{ team_name = \"${teamName}\"; worker = \"<your-worker-name>\" } | ConvertTo-Json -Compress\\`\n   \\`omx team api mailbox-list --input $payload --json\\`\n2. Mark delivered:\n   \\`$payload = @{ team_name = \"${teamName}\"; worker = \"<your-worker-name>\"; message_id = \"<MESSAGE_ID>\" } | ConvertTo-Json -Compress\\`\n   \\`omx team api mailbox-mark-delivered --input $payload --json\\`",
].join("\n");

const bootstrapPreview = patchWorkerBootstrap(workerBootstrapSample);
assert.equal(bootstrapPreview.changed, true);
assert.equal(bootstrapPreview.status, "patched");
assert.match(bootstrapPreview.content, new RegExp(PATCH_MARKER));
assert.match(bootstrapPreview.content, /function buildRawTeamApiPayload/);
assert.match(bootstrapPreview.content, /buildRawTeamApiExample\("send-message"/);
assert.doesNotMatch(bootstrapPreview.content, /send-message --input \$payload/);
assert.doesNotMatch(bootstrapPreview.content, /mailbox-list --input \$payload/);

const skillSample = [
  "Windows durable-worker wrapper:",
  "",
  "```powershell",
  'omx-team-send-message.ps1 -TeamName "<teamName>" -FromWorker "<workerName>" -ToWorker "leader-fixed" -Body "ACK: <workerName> initialized" -Json',
  "```",
  "",
  "Copy/paste template:",
  "",
  "```bash",
  'omx team api send-message --input "{\\"team_name\\":\\"<teamName>\\",\\"from_worker\\":\\"<workerName>\\",\\"to_worker\\":\\"leader-fixed\\",\\"body\\":\\"ACK: <workerName> initialized\\"}" --json',
  "```",
  "",
  "Windows durable-worker wrappers:",
  '- `omx-team-mailbox-list.ps1 -TeamName "<teamName>" -Worker "<workerName>" -Json`',
  '- `omx-team-mailbox-mark-delivered.ps1 -TeamName "<teamName>" -Worker "<workerName>" -MessageId "<MESSAGE_ID>" -Json`',
  "",
  "```bash",
  'omx team api mailbox-list --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\"}" --json',
  'omx team api mailbox-mark-delivered --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\",\\"message_id\\":\\"<MESSAGE_ID>\\"}" --json',
  "```",
].join("\n");

const skillPreview = patchWorkerSkill(skillSample);
assert.equal(skillPreview.changed, true);
assert.equal(skillPreview.status, "patched");
assert.match(skillPreview.content, new RegExp(PATCH_MARKER));
assert.match(skillPreview.content, /raw JSON example intentionally omitted here/);
assert.doesNotMatch(skillPreview.content, /omx team api send-message --input "\{/);
assert.doesNotMatch(skillPreview.content, /omx team api mailbox-list --input "\{/);

console.log("openclaw-omx-worker-visible-raw-abstraction-fix: ok");
