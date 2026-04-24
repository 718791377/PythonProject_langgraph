import assert from "node:assert/strict";
import {
  PATCH_MARKER,
  patchWorkerBootstrapLifecycleGuidance,
  patchWorkerSkillLifecycleGuidance,
} from "../tools/openclaw-omx-windows-lifecycle-wrapper-guidance-fix.mjs";

const bootstrapSample = [
  "8. Use claim-safe lifecycle APIs only:",
  '   - \\`omx team api claim-task --json\\`',
  '   - \\`omx team api transition-task-status --json\\`',
  '   - \\`omx team api release-task-claim --json\\` only for rollback to pending',
  '9. Request a claim via CLI interop (\\`omx team api claim-task --json\\`) to claim it, unless the task is already claimed by your worker.',
  '12. Complete/fail it via lifecycle transition API (\\`omx team api transition-task-status --json\\`) from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`)',
  '13. Use \\`omx team api release-task-claim --json\\` only for rollback to \\`pending\\`',
  '3. Request a claim via CLI interop (\\`omx team api claim-task --json\\`)',
  '6. Complete/fail via lifecycle transition API (\\`omx team api transition-task-status --json\\`) from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`)',
  '7. Use \\`omx team api release-task-claim --json\\` only for rollback to \\`pending\\`',
  '7. Request a claim via CLI interop (\\`omx team api claim-task --json\\`); do not directly set lifecycle fields in the task file',
  '10. On completion/failure, use lifecycle transition APIs:',
  '   - \\`omx team api transition-task-status --json\\` with from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\`',
  '11. Use \\`omx team api release-task-claim --json\\` only for rollback/requeue to \\`pending\\` (not for completion)',
  '',
].join("\n");

const bootstrapPreview = patchWorkerBootstrapLifecycleGuidance(bootstrapSample);
assert.equal(bootstrapPreview.changed, true);
assert.equal(bootstrapPreview.status, "patched");
assert.match(bootstrapPreview.content, new RegExp(PATCH_MARKER));
assert.match(bootstrapPreview.content, /omx-team-claim-task\.ps1/);
assert.match(bootstrapPreview.content, /omx-team-transition-task-status\.ps1/);
assert.match(bootstrapPreview.content, /omx-team-release-task-claim\.ps1/);

const skillSample = `
6. Claim the task (do NOT start work without a claim) using claim-safe lifecycle CLI interop (\`omx team api claim-task --json\`).
8. Complete/fail the task via lifecycle transition CLI interop (\`omx team api transition-task-status --json\`) from \`in_progress\` to \`completed\` or \`failed\`.
9. Use \`omx team api release-task-claim --json\` only for rollback/requeue to \`pending\` (not for completion).
`;

const skillPreview = patchWorkerSkillLifecycleGuidance(skillSample);
assert.equal(skillPreview.changed, true);
assert.equal(skillPreview.status, "patched");
assert.match(skillPreview.content, /omx-team-claim-task\.ps1/);
assert.match(skillPreview.content, /omx-team-transition-task-status\.ps1/);
assert.match(skillPreview.content, /omx-team-release-task-claim\.ps1/);

console.log("openclaw-omx-windows-lifecycle-wrapper-guidance-fix: ok");
