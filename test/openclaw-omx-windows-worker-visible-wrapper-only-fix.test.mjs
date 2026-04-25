import assert from "node:assert/strict";
import {
  PATCH_MARKER,
  patchWorkerBootstrapVisibleGuidance,
  patchWorkerSkillVisibleGuidance,
} from "../tools/openclaw-omx-windows-worker-visible-wrapper-only-fix.mjs";

const bootstrapSample = [
  '3. Send an ACK to the lead using CLI interop \\`omx team api send-message --json\\` (to_worker="leader-fixed") once initialized',
  '5. On native Windows, do **not** wrap \\`omx team api\\` commands inside \\`cmd /c\\`, and do **not** inline raw JSON directly into \\`--input\\`; use a PowerShell variable or file-backed JSON only.',
  '15. For legacy team_* MCP tools (hard-deprecated), switch to \\`omx team api\\` CLI interop; do not pass workingDirectory unless the lead explicitly tells you to',
  'When calling \\`omx team api send-message\\`, you MUST always include:',
  'Example:\n// OPENCLAW_OMX_WINDOWS_WORKER_BOOTSTRAP_MAILBOX_EXAMPLE_FIX_V1\n$payload = @{ team_name = "${teamName}"; from_worker = "<your-worker-name>"; to_worker = "leader-fixed"; body = "ACK: <your-worker-name> initialized" } | ConvertTo-Json -Compress\nomx team api send-message --input $payload --json',
  '1. Read:\n   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>" } | ConvertTo-Json -Compress\\`\n   \\`omx team api mailbox-list --input $payload --json\\`\n2. Mark delivered:\n   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress\\`\n   \\`omx team api mailbox-mark-delivered --input $payload --json\\`',
].join("\n");

const bootstrapPreview = patchWorkerBootstrapVisibleGuidance(bootstrapSample);
assert.equal(bootstrapPreview.changed, true);
assert.match(bootstrapPreview.content, new RegExp(PATCH_MARKER));
assert.match(bootstrapPreview.content, /omx-team-send-message\.ps1/);
assert.match(bootstrapPreview.content, /omx-team-mailbox-list\.ps1/);
assert.doesNotMatch(bootstrapPreview.content, /send-message --input \$payload/);

const skillSample = [
  '- On Windows, prefer the generated `omx-team-send-message.ps1` / `omx-team-mailbox-list.ps1` / `omx-team-mailbox-mark-delivered.ps1` wrapper scripts instead of hand-writing `omx team api --input ...` payloads.',
  'Copy/paste template:\n\n```bash\nomx team api send-message --input "{\\"team_name\\":\\"<teamName>\\",\\"from_worker\\":\\"<workerName>\\",\\"to_worker\\":\\"leader-fixed\\",\\"body\\":\\"ACK: <workerName> initialized\\"}" --json\n```',
  '6. Claim the task (do NOT start work without a claim). On Windows, prefer `omx-team-claim-task.ps1 -TeamName "<teamName>" -TaskId "<id>" -Worker "<workerName>" -Json`; on other platforms, use `omx team api claim-task --json`. // OPENCLAW_OMX_WINDOWS_LIFECYCLE_WRAPPER_GUIDANCE_FIX_V1',
  '8. Complete/fail the task via lifecycle transition CLI interop. On Windows, prefer `omx-team-transition-task-status.ps1 -TeamName "<teamName>" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json`; on other platforms, use `omx team api transition-task-status --json`.',
  '9. Use `omx-team-release-task-claim.ps1 -TeamName "<teamName>" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<workerName>" -Json` on Windows, or `omx team api release-task-claim --json` on other platforms, only for rollback/requeue to `pending` (not for completion).',
  'Use CLI interop:\n- `omx team api mailbox-list --json` to read\n- `omx team api mailbox-mark-delivered --json` to acknowledge delivery\n\nCopy/paste templates:\n\n```bash\nomx team api mailbox-list --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\"}" --json\nomx team api mailbox-mark-delivered --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\",\\"message_id\\":\\"<MESSAGE_ID>\\"}" --json\n```',
  '- Prefer inbox/mailbox/task state and `omx team api ... --json` operations.',
].join("\n\n");

const skillPreview = patchWorkerSkillVisibleGuidance(skillSample);
assert.equal(skillPreview.changed, true);
assert.match(skillPreview.content, new RegExp(PATCH_MARKER));
assert.match(skillPreview.content, /omx-team-send-message\.ps1/);
assert.match(skillPreview.content, /Windows durable-worker wrappers/);
assert.doesNotMatch(skillPreview.content, /omx team api send-message --input "\{/);

console.log("openclaw-omx-windows-worker-visible-wrapper-only-fix: ok");
