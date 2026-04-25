import assert from "node:assert/strict";
import { patchCommandStyleGuidance, PATCH_MARKER } from "../tools/openclaw-omx-windows-command-style-guidance-fix.mjs";

const sample = `
5. On native Windows, do **not** wrap \`omx team api\` commands inside \`cmd /c\`, and do **not** inline raw JSON directly into \`--input\`; use a PowerShell variable or file-backed JSON only.

Windows PowerShell:

\`\`\`powershell
omx team api send-message --input (@{ team_name = "<teamName>"; from_worker = "<workerName>"; to_worker = "leader-fixed"; body = "ACK: <workerName> initialized" } | ConvertTo-Json -Compress) --json
\`\`\`
`;

const preview = patchCommandStyleGuidance(sample);
assert.equal(preview.changed, true);
assert.equal(preview.status, "patched");
assert.match(preview.content, new RegExp(PATCH_MARKER));
assert.match(preview.content, /Never create a separate `\$payload` variable/);
assert.match(preview.content, /On Windows, use the direct one-line --input/);

const second = patchCommandStyleGuidance(preview.content);
assert.equal(second.changed, false);
assert.equal(second.status, "already_patched");

console.log("openclaw-omx-windows-command-style-guidance-fix: ok");
