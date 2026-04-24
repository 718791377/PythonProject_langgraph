import assert from "node:assert/strict";
import { PATCH_MARKER, patchWorkerBootstrap, patchWorkerSkill } from "../tools/openclaw-omx-windows-worker-wrapper-guidance-fix.mjs";

const workerBootstrapSample = `
function buildSendMessageExample(teamName, workerName) {
    if (process.platform === 'win32') {
        return \`omx team api send-message --input (@{ team_name = "\${teamName}"; from_worker = "\${workerName}"; to_worker = "leader-fixed"; body = "ACK: \${workerName} initialized" } | ConvertTo-Json -Compress) --json\`;
    }
}
function buildMailboxListExample(teamName, workerName) {
    if (process.platform === 'win32') {
        return \`omx team api mailbox-list --input (@{ team_name = "\${teamName}"; worker = "\${workerName}" } | ConvertTo-Json -Compress) --json\`;
    }
}
function buildMailboxDeliveredExample(teamName, workerName) {
    if (process.platform === 'win32') {
        return \`omx team api mailbox-mark-delivered --input (@{ team_name = "\${teamName}"; worker = "\${workerName}"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress) --json\`;
    }
}
5. On native Windows, do **not** wrap \`omx team api\` commands inside \`cmd /c\`, and do **not** inline raw JSON directly into \`--input\`; use a PowerShell variable or file-backed JSON only.
`;

const bootstrapPreview = patchWorkerBootstrap(workerBootstrapSample);
assert.equal(bootstrapPreview.changed, true);
assert.equal(bootstrapPreview.status, "patched");
assert.match(bootstrapPreview.content, new RegExp(PATCH_MARKER));
assert.match(bootstrapPreview.content, /omx-team-send-message\.ps1/);
assert.match(bootstrapPreview.content, /omx-team-mailbox-list\.ps1/);
assert.match(bootstrapPreview.content, /omx-team-mailbox-mark-delivered\.ps1/);

const skillSample = `
Use CLI interop:
- \`omx team api send-message --input <json> --json\` with {team_name, from_worker, to_worker:"leader-fixed", body}

Windows PowerShell:

\`\`\`powershell
# OPENCLAW_OMX_WORKER_SKILL_POWERSHELL_ONELINER_FIX_V1
omx team api send-message --input (@{ team_name = "<teamName>"; from_worker = "<workerName>"; to_worker = "leader-fixed"; body = "ACK: <workerName> initialized" } | ConvertTo-Json -Compress) --json
\`\`\`

Windows PowerShell:

\`\`\`powershell
omx team api mailbox-list --input (@{ team_name = "<teamName>"; worker = "<workerName>" } | ConvertTo-Json -Compress) --json
omx team api mailbox-mark-delivered --input (@{ team_name = "<teamName>"; worker = "<workerName>"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress) --json
\`\`\`
`;

const skillPreview = patchWorkerSkill(skillSample);
assert.equal(skillPreview.changed, true);
assert.equal(skillPreview.status, "patched");
assert.match(skillPreview.content, new RegExp(PATCH_MARKER));
assert.match(skillPreview.content, /omx-team-send-message\.ps1/);
assert.match(skillPreview.content, /omx-team-mailbox-list\.ps1/);
assert.doesNotMatch(skillPreview.content, /omx team api send-message --input \(@\{/);

console.log("openclaw-omx-windows-worker-wrapper-guidance-fix: ok");
