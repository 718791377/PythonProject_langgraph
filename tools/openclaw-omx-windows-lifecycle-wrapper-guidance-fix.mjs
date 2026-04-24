import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-lifecycle-wrapper-guidance-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_LIFECYCLE_WRAPPER_GUIDANCE_FIX_V1";

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

export function patchWorkerBootstrapLifecycleGuidance(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const replacements = [
    [
      '   - \\`omx team api claim-task --json\\`',
      '   - \\`omx-team-claim-task.ps1 -TeamName "${options.teamName}" -TaskId "<id>" -Worker "${options.workerName}" -Json\\` // ' + PATCH_MARKER,
    ],
    [
      '   - \\`omx team api transition-task-status --json\\`',
      '   - \\`omx-team-transition-task-status.ps1 -TeamName "${options.teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`',
    ],
    [
      '   - \\`omx team api release-task-claim --json\\` only for rollback to pending',
      '   - \\`omx-team-release-task-claim.ps1 -TeamName "${options.teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "${options.workerName}" -Json\\` only for rollback to pending',
    ],
    [
      '9. Request a claim via CLI interop (\\`omx team api claim-task --json\\`) to claim it, unless the task is already claimed by your worker.',
      '9. On Windows, request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "<id>" -Worker "${workerName}" -Json\\`; on other platforms, use \\`omx team api claim-task --json\\`. Claim it unless the task is already claimed by your worker.',
    ],
    [
      '12. Complete/fail it via lifecycle transition API (\\`omx team api transition-task-status --json\\`) from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`)',
      '12. On Windows, complete/fail via \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`; on other platforms, use \\`omx team api transition-task-status --json\\`. Transition from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`).',
    ],
    [
      '13. Use \\`omx team api release-task-claim --json\\` only for rollback to \\`pending\\`',
      '13. On Windows, use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "${workerName}" -Json\\` only for rollback to \\`pending\\`; on other platforms, use \\`omx team api release-task-claim --json\\`.',
    ],
    [
      '3. Request a claim via CLI interop (\\`omx team api claim-task --json\\`)',
      '3. On Windows, request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -Worker "${workerName}" -Json\\`; on other platforms, use \\`omx team api claim-task --json\\`.',
    ],
    [
      '6. Complete/fail via lifecycle transition API (\\`omx team api transition-task-status --json\\`) from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\` (include \\`result\\`/\\`error\\`)',
      '6. On Windows, complete/fail via \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\`; on other platforms, use \\`omx team api transition-task-status --json\\`.',
    ],
    [
      '7. Use \\`omx team api release-task-claim --json\\` only for rollback to \\`pending\\`',
      '7. On Windows, use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "${taskId}" -ClaimToken "<CLAIM_TOKEN>" -Worker "${workerName}" -Json\\` only for rollback to \\`pending\\`; on other platforms, use \\`omx team api release-task-claim --json\\`.',
    ],
    [
      '7. Request a claim via CLI interop (\\`omx team api claim-task --json\\`); do not directly set lifecycle fields in the task file',
      '7. On Windows, request a claim via \\`omx-team-claim-task.ps1 -TeamName "${teamName}" -TaskId "<id>" -Worker "<your-worker-name>" -Json\\`; on other platforms, use \\`omx team api claim-task --json\\`. Do not directly set lifecycle fields in the task file.',
    ],
    [
      '10. On completion/failure, use lifecycle transition APIs:',
      '10. On completion/failure, use lifecycle transition APIs (on Windows, prefer the generated wrapper scripts):',
    ],
    [
      '   - \\`omx team api transition-task-status --json\\` with from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\`',
      '   - \\`omx-team-transition-task-status.ps1 -TeamName "${teamName}" -TaskId "<id>" -From in_progress -To completed -ClaimToken "<CLAIM_TOKEN>" -Result "<RESULT>" -Json\\` on Windows; otherwise \\`omx team api transition-task-status --json\\` with from \\`"in_progress"\\` to \\`"completed"\\` or \\`"failed"\\`',
    ],
    [
      '11. Use \\`omx team api release-task-claim --json\\` only for rollback/requeue to \\`pending\\` (not for completion)',
      '11. Use \\`omx-team-release-task-claim.ps1 -TeamName "${teamName}" -TaskId "<id>" -ClaimToken "<CLAIM_TOKEN>" -Worker "<your-worker-name>" -Json\\` on Windows, or \\`omx team api release-task-claim --json\\` on other platforms, only for rollback/requeue to \\`pending\\` (not for completion)',
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

export function patchWorkerSkillLifecycleGuidance(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const replacements = [
    [
      "6. Claim the task (do NOT start work without a claim) using claim-safe lifecycle CLI interop (`omx team api claim-task --json`).",
      "6. Claim the task (do NOT start work without a claim). On Windows, prefer `omx-team-claim-task.ps1 -TeamName \"<teamName>\" -TaskId \"<id>\" -Worker \"<workerName>\" -Json`; on other platforms, use `omx team api claim-task --json`. // " + PATCH_MARKER,
    ],
    [
      "8. Complete/fail the task via lifecycle transition CLI interop (`omx team api transition-task-status --json`) from `in_progress` to `completed` or `failed`.",
      "8. Complete/fail the task via lifecycle transition CLI interop. On Windows, prefer `omx-team-transition-task-status.ps1 -TeamName \"<teamName>\" -TaskId \"<id>\" -From in_progress -To completed -ClaimToken \"<CLAIM_TOKEN>\" -Result \"<RESULT>\" -Json`; on other platforms, use `omx team api transition-task-status --json`.",
    ],
    [
      "9. Use `omx team api release-task-claim --json` only for rollback/requeue to `pending` (not for completion).",
      "9. Use `omx-team-release-task-claim.ps1 -TeamName \"<teamName>\" -TaskId \"<id>\" -ClaimToken \"<CLAIM_TOKEN>\" -Worker \"<workerName>\" -Json` on Windows, or `omx team api release-task-claim --json` on other platforms, only for rollback/requeue to `pending` (not for completion).",
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
    { path: defaultWorkerBootstrapPath(), patchFn: patchWorkerBootstrapLifecycleGuidance },
    { path: defaultWorkerSkillPath(), patchFn: patchWorkerSkillLifecycleGuidance },
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
