import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-worker-visible-wrapper-only-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_WORKER_VISIBLE_WRAPPER_ONLY_FIX_V1";

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

export function patchWorkerBootstrapVisibleGuidance(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const replacements = [
    [
      '3. Send an ACK to the lead using CLI interop \\`omx team api send-message --json\\` (to_worker="leader-fixed") once initialized',
      '3. On Windows durable worker lanes, send the startup ACK through \\`omx-team-send-message.ps1\\` (to_worker="leader-fixed") once initialized. // ' + PATCH_MARKER,
    ],
    [
      '5. On native Windows, do **not** wrap \\`omx team api\\` commands inside \\`cmd /c\\`, and do **not** inline raw JSON directly into \\`--input\\`; use a PowerShell variable or file-backed JSON only.',
      '5. On native Windows durable worker lanes, use only the generated \\`omx-team-*.ps1\\` wrapper scripts for mailbox and lifecycle actions. Do **not** hand-write raw \\`omx team api --input ...\\` payloads.',
    ],
    [
      '15. For legacy team_* MCP tools (hard-deprecated), switch to \\`omx team api\\` CLI interop; do not pass workingDirectory unless the lead explicitly tells you to',
      '15. For durable worker mailbox and lifecycle actions on Windows, prefer the generated \\`omx-team-*.ps1\\` wrappers. Use direct \\`omx team api\\` calls only for manual troubleshooting outside the normal worker loop.',
    ],
    [
      'When calling \\`omx team api send-message\\`, you MUST always include:',
      'When sending a leader or peer message, you MUST always include:',
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
      '- On Windows, prefer the generated `omx-team-send-message.ps1` / `omx-team-mailbox-list.ps1` / `omx-team-mailbox-mark-delivered.ps1` wrapper scripts instead of hand-writing `omx team api --input ...` payloads.',
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
      [
        'Windows durable-worker wrapper:',
        '',
        '```powershell',
        'omx-team-send-message.ps1 -TeamName "<teamName>" -FromWorker "<workerName>" -ToWorker "leader-fixed" -Body "ACK: <workerName> initialized" -Json',
        '```',
      ].join("\n"),
    ],
    [
      '6. Claim the task (do NOT start work without a claim). On Windows, prefer `omx-team-claim-task.ps1 -TeamName "<teamName>" -TaskId "<id>" -Worker "<workerName>" -Json`; on other platforms, use `omx team api claim-task --json`. // OPENCLAW_OMX_WINDOWS_LIFECYCLE_WRAPPER_GUIDANCE_FIX_V1',
      '6. Claim the task (do NOT start work without a claim). On Windows durable worker lanes, use `omx-team-claim-task.ps1 -TeamName "<teamName>" -TaskId "<id>" -Worker "<workerName>" -Json`.',
    ],
    [
      '8. Complete/fail the task via lifecycle transition CLI interop. On Windows, prefer `omx-team-transition-task-status.ps1 -TeamName "<teamName>" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json`; on other platforms, use `omx team api transition-task-status --json`.',
      '8. Complete/fail the task via lifecycle transition CLI interop. On Windows durable worker lanes, use `omx-team-transition-task-status.ps1 -TeamName "<teamName>" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json`.',
    ],
    [
      '9. Use `omx-team-release-task-claim.ps1 -TeamName "<teamName>" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<workerName>" -Json` on Windows, or `omx team api release-task-claim --json` on other platforms, only for rollback/requeue to `pending` (not for completion).',
      '9. Use `omx-team-release-task-claim.ps1 -TeamName "<teamName>" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<workerName>" -Json` on Windows durable worker lanes only for rollback/requeue to `pending` (not for completion).',
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
      '- Prefer inbox/mailbox/task state and `omx team api ... --json` operations.',
      '- On Windows durable worker lanes, prefer inbox/mailbox/task state plus the generated `omx-team-*.ps1` wrapper scripts.',
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
