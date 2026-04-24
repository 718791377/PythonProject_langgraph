import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-worker-wrapper-only-guidance-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_WORKER_WRAPPER_ONLY_GUIDANCE_FIX_V1";

function defaultWorkerBootstrapPath() {
  const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
  return path.join(
    appData,
    "npm",
    "node_modules",
    "oh-my-codex",
    "dist",
    "team",
    "worker-bootstrap.js",
  );
}

function defaultWorkerSkillPath() {
  return path.join(os.homedir(), ".codex", "skills", "worker", "SKILL.md");
}

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function ensureDir(dirPath) {
  await fs.mkdir(dirPath, { recursive: true });
}

function nowTag() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

export function patchWorkerBootstrapGuidance(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const replacements = [
    [
      '3. Send an ACK to the lead using CLI interop \\`omx team api send-message --json\\` (to_worker="leader-fixed") once initialized',
      '3. Send an ACK to the lead through \\`omx-team-send-message.ps1\\` (to_worker="leader-fixed") once initialized // ' + PATCH_MARKER,
    ],
    [
      '7. On Windows, request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "<id>" -Worker "<your-worker-name>" -Json\\`; on other platforms, use \\`omx team api claim-task --json\\`. Do not directly set lifecycle fields in the task file.',
      '7. Request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "<id>" -Worker "<your-worker-name>" -Json\\`. Do not directly set lifecycle fields in the task file.',
    ],
    [
      '10. On completion/failure, use lifecycle transition APIs (on Windows, prefer the generated wrapper scripts):',
      '10. On completion/failure, use the generated lifecycle wrapper scripts:',
    ],
    [
      '   - \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\` on Windows; otherwise \\`omx team api transition-task-status --json\\` with from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\`',
      '   - \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\` with from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\`',
    ],
    [
      '11. Use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<your-worker-name>" -Json\\` on Windows, or \\`omx team api release-task-claim --json\\` on other platforms, only for rollback/requeue to \\`pending\\` (not for completion)',
      '11. Use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<your-worker-name>" -Json\\` only for rollback/requeue to \\`pending\\` (not for completion)',
    ],
    [
      '15. For legacy team_* MCP tools (hard-deprecated), switch to \\`omx team api\\` CLI interop; do not pass workingDirectory unless the lead explicitly tells you to',
      '15. For normal Windows worker execution, use the generated \\`omx-team-*.ps1\\` wrappers. Reserve raw \\`omx team api\\` CLI interop for manual troubleshooting only.',
    ],
    [
      'When calling \\`omx team api send-message\\`, you MUST always include:',
      'When sending a message through \\`omx-team-send-message.ps1\\`, you MUST always provide:',
    ],
    [
      [
        'Example:',
        '// OPENCLAW_OMX_WINDOWS_WORKER_BOOTSTRAP_MAILBOX_EXAMPLE_FIX_V1',
        '$payload = @{ team_name = "${teamName}"; from_worker = "<your-worker-name>"; to_worker = "leader-fixed"; body = "ACK: <your-worker-name> initialized" } | ConvertTo-Json -Compress',
        'omx team api send-message --input $payload --json',
      ].join("\n"),
      [
        'Example:',
        '// ' + PATCH_MARKER,
        'omx-team-send-message.ps1 -TeamName "${teamName}" -FromWorker "<your-worker-name>" -ToWorker "leader-fixed" -Body "ACK: <your-worker-name> initialized" -Json',
      ].join("\n"),
    ],
    [
      [
        '1. Read:',
        '   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>" } | ConvertTo-Json -Compress\\`',
        '   \\`omx team api mailbox-list --input $payload --json\\`',
        '2. Mark delivered:',
        '   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress\\`',
        '   \\`omx team api mailbox-mark-delivered --input $payload --json\\`',
      ].join("\n"),
      [
        '1. Read:',
        '   \\`omx-team-mailbox-list.ps1 -TeamName "${teamName}" -Worker "<your-worker-name>" -Json\\`',
        '2. Mark delivered:',
        '   \\`omx-team-mailbox-mark-delivered.ps1 -TeamName "${teamName}" -Worker "<your-worker-name>" -MessageId "<MESSAGE_ID>" -Json\\`',
      ].join("\n"),
    ],
    [
      '9. On Windows, request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "<id>" -Worker "${workerName}" -Json\\`; on other platforms, use \\`omx team api claim-task --json\\`. Claim it unless the task is already claimed by your worker.',
      '9. Request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "<id>" -Worker "${workerName}" -Json\\`. Claim it unless the task is already claimed by your worker.',
    ],
    [
      '12. On Windows, complete/fail via \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`; on other platforms, use \\`omx team api transition-task-status --json\\`. Transition from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`).',
      '12. Complete/fail via \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`. Transition from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`).',
    ],
    [
      '13. On Windows, use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "${workerName}" -Json\\` only for rollback to \\`pending\\`; on other platforms, use \\`omx team api release-task-claim --json\\`.',
      '13. Use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "${workerName}" -Json\\` only for rollback to \\`pending\\`.',
    ],
    [
      '16. For legacy team_* MCP tools (hard-deprecated), use \\`omx team api\\`; do not pass \\`workingDirectory\\` unless the lead explicitly asks (if resolution fails, use leader cwd: \\`${leaderCwd}\\`)',
      '16. For normal Windows worker execution, use the generated \\`omx-team-*.ps1\\` wrappers. Reserve raw \\`omx team api\\` CLI interop for manual troubleshooting only (if resolution fails, use leader cwd: \\`${leaderCwd}\\`).',
    ],
    [
      '3. On Windows, request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -Worker "${workerName}" -Json\\`; on other platforms, use \\`omx team api claim-task --json\\`.',
      '3. Request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -Worker "${workerName}" -Json\\`.',
    ],
    [
      '6. On Windows, complete/fail via \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`; on other platforms, use \\`omx team api transition-task-status --json\\`.',
      '6. Complete/fail via \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`.',
    ],
    [
      '7. On Windows, use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -ClaimToken "<CLAIM_TOKEN>" -Worker "${workerName}" -Json\\` only for rollback to \\`pending\\`; on other platforms, use \\`omx team api release-task-claim --json\\`.',
      '7. Use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -ClaimToken "<CLAIM_TOKEN>" -Worker "${workerName}" -Json\\` only for rollback to \\`pending\\`.',
    ],
  ];

  let content = raw;
  let changed = false;
  for (const [from, to] of replacements) {
    if (content.includes(from)) {
      content = content.replace(from, to);
      changed = true;
    }
  }
  return { changed, status: changed ? "patched" : "no_known_guidance_anchor", content };
}

export function patchWorkerSkillVisibleGuidance(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const replacements = [
    [
      '- On Windows durable worker lanes, use only the generated `omx-team-*.ps1` wrapper scripts for messaging, mailbox, and lifecycle actions. // OPENCLAW_OMX_WINDOWS_WORKER_VISIBLE_WRAPPER_ONLY_FIX_V1',
      '- On Windows durable worker lanes, use only the generated `omx-team-*.ps1` wrapper scripts for messaging, mailbox, and lifecycle actions. // ' + PATCH_MARKER,
    ],
    [
      [
        'Copy/paste template:',
        '',
        '```bash',
        'omx team api send-message --input "{\\"team_name\\":\\"<teamName>\\",\\"from_worker\\":\\"<workerName>\\",\\"to_worker\\":\\"leader-fixed\\",\\"body\\":\\"ACK: <workerName> initialized\\"}" --json',
        '```',
      ].join("\n"),
      'Non-Windows fallback examples are intentionally omitted from the Windows worker skill surface.',
    ],
    [
      '6. Claim the task (do NOT start work without a claim). On Windows durable worker lanes, use `omx-team-claim-task.ps1 -TeamName "<teamName>" -TaskId "<id>" -Worker "<workerName>" -Json`.',
      '6. Claim the task (do NOT start work without a claim). Use `omx-team-claim-task.ps1 -TeamName "<teamName>" -TaskId "<id>" -Worker "<workerName>" -Json` on Windows durable worker lanes.',
    ],
    [
      '8. Complete/fail the task via lifecycle transition CLI interop. On Windows durable worker lanes, use `omx-team-transition-task-status.ps1 -TeamName "<teamName>" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json`.',
      '8. Complete/fail the task via lifecycle transition CLI interop. Use `omx-team-transition-task-status.ps1 -TeamName "<teamName>" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json` on Windows durable worker lanes.',
    ],
    [
      '9. Use `omx-team-release-task-claim.ps1 -TeamName "<teamName>" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<workerName>" -Json` on Windows durable worker lanes only for rollback/requeue to `pending` (not for completion).',
      '9. Use `omx-team-release-task-claim.ps1 -TeamName "<teamName>" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<workerName>" -Json` only for rollback/requeue to `pending` (not for completion) on Windows durable worker lanes.',
    ],
    [
      [
        'Use CLI interop:',
        '- `omx team api mailbox-list --json` to read',
        '- `omx team api mailbox-mark-delivered --json` to acknowledge delivery',
        '',
        'Copy/paste templates:',
        '',
        '```bash',
        'omx team api mailbox-list --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\"}" --json',
        'omx team api mailbox-mark-delivered --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\",\\"message_id\\":\\"<MESSAGE_ID>\\"}" --json',
        '```',
      ].join("\n"),
      [
        'Windows durable-worker wrappers:',
        '- `omx-team-mailbox-list.ps1 -TeamName "<teamName>" -Worker "<workerName>" -Json`',
        '- `omx-team-mailbox-mark-delivered.ps1 -TeamName "<teamName>" -Worker "<workerName>" -MessageId "<MESSAGE_ID>" -Json`',
      ].join("\n"),
    ],
    [
      '- On Windows durable worker lanes, prefer inbox/mailbox/task state plus the generated `omx-team-*.ps1` wrapper scripts.',
      '- On Windows durable worker lanes, prefer inbox/mailbox/task state plus the generated `omx-team-*.ps1` wrapper scripts. Avoid raw `omx team api` examples unless you are manually debugging.',
    ],
  ];

  let content = raw;
  let changed = false;
  for (const [from, to] of replacements) {
    if (content.includes(from)) {
      content = content.replace(from, to);
      changed = true;
    }
  }

  return { changed, status: changed ? "patched" : "no_known_guidance_anchor", content };
}

async function inspectOne(filePath, backupDir) {
  const targetExists = await exists(filePath);
  if (!targetExists) {
    return { ok: false, targetPath: filePath, backupDir, exists: false, patched: false, backupCount: 0, patchMarker: PATCH_MARKER };
  }
  const raw = await fs.readFile(filePath, "utf8");
  let backupCount = 0;
  if (await exists(backupDir)) {
    const entries = await fs.readdir(backupDir, { withFileTypes: true });
    const basename = path.basename(filePath);
    backupCount = entries.filter((entry) => entry.isFile() && entry.name.startsWith(`${basename}.`) && entry.name.endsWith(".bak")).length;
  }
  return { ok: true, targetPath: filePath, backupDir, exists: true, patched: raw.includes(PATCH_MARKER), patchMarker: PATCH_MARKER, backupCount };
}

async function applyOne(filePath, backupDir, patchFn) {
  if (!(await exists(filePath))) {
    return { ok: false, targetPath: filePath, backupDir, status: "missing_target", changed: false };
  }
  const raw = await fs.readFile(filePath, "utf8");
  const patchResult = patchFn(raw);
  if (!patchResult.changed) {
    return { ok: patchResult.status === "already_patched", targetPath: filePath, backupDir, status: patchResult.status, changed: false, patchMarker: PATCH_MARKER };
  }
  await ensureDir(backupDir);
  const backupPath = path.join(backupDir, `${path.basename(filePath)}.${nowTag()}.bak`);
  await fs.writeFile(backupPath, raw, "utf8");
  await fs.writeFile(filePath, patchResult.content, "utf8");
  return { ok: true, targetPath: filePath, backupDir, backupPath, status: patchResult.status, changed: true, patchMarker: PATCH_MARKER };
}

async function restoreOne(filePath, backupDir) {
  if (!(await exists(backupDir))) {
    return { ok: false, targetPath: filePath, backupDir, status: "backup_missing", changed: false };
  }
  const basename = path.basename(filePath);
  const entries = await fs.readdir(backupDir, { withFileTypes: true });
  const candidates = entries.filter((entry) => entry.isFile() && entry.name.startsWith(`${basename}.`) && entry.name.endsWith(".bak")).map((entry) => path.join(backupDir, entry.name)).sort();
  const latestBackup = candidates.at(-1);
  if (!latestBackup) {
    return { ok: false, targetPath: filePath, backupDir, status: "backup_missing", changed: false };
  }
  const backupRaw = await fs.readFile(latestBackup, "utf8");
  await fs.writeFile(filePath, backupRaw, "utf8");
  return { ok: true, targetPath: filePath, backupDir, backupPath: latestBackup, status: "restored", changed: true };
}

function print(payload, json = false) {
  if (json) {
    process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
    return;
  }
  for (const [key, value] of Object.entries(payload)) {
    process.stdout.write(`${key}=${typeof value === "string" ? value : JSON.stringify(value)}\n`);
  }
}

async function main(argv = process.argv.slice(2)) {
  const json = argv.includes("--json");
  const args = argv.filter((arg) => arg !== "--json");
  const command = args[0] || "status";
  const targets = [
    { path: defaultWorkerBootstrapPath(), patchFn: patchWorkerBootstrapVisibleGuidance },
    { path: defaultWorkerSkillPath(), patchFn: patchWorkerSkillVisibleGuidance },
  ];
  const results = [];
  for (const target of targets) {
    const backupDir = path.join(DEFAULT_BACKUP_DIR, path.basename(target.path));
    if (command === "status") results.push(await inspectOne(target.path, backupDir));
    else if (command === "apply") results.push(await applyOne(target.path, backupDir, target.patchFn));
    else if (command === "restore") results.push(await restoreOne(target.path, backupDir));
    else throw new Error(`unknown command: ${command}`);
  }
  print({ ok: results.every((r) => r.ok !== false), results }, json);
}

const invokedAsScript = (() => {
  try {
    return process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
  } catch {
    return false;
  }
})();

if (invokedAsScript) {
  main().catch((error) => {
    process.stderr.write(`${String(error?.stack || error)}\n`);
    process.exitCode = 1;
  });
}
