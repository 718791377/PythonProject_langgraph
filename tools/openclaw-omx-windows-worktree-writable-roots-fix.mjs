import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-worktree-writable-roots-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_WORKTREE_WRITABLE_ROOTS_FIX_V1";

function defaultRuntimePath() {
  const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
  return path.join(
    appData,
    "npm",
    "node_modules",
    "oh-my-codex",
    "dist",
    "team",
    "runtime.js",
  );
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

export function patchWorktreeWritableRoots(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }
  const anchor =
    /const workerLaunchArgs = resolveWorkerLaunchArgsFromEnv\(process\.env, workerRole, undefined, preferredReasoning, workerCliPlan\[i - 1\]\);\s*const resolvedWorkerModel = parseTeamWorkerLaunchArgs\(workerLaunchArgs\)\.modelOverride \?\? undefined;/m;
  if (!anchor.test(raw)) {
    return { changed: false, status: "anchor_missing", content: raw };
  }
  const replacement = [
    "const workerLaunchArgsBase = resolveWorkerLaunchArgsFromEnv(process.env, workerRole, undefined, preferredReasoning, workerCliPlan[i - 1]);",
    "            const workerLaunchArgs = [...workerLaunchArgsBase];",
    `            // ${PATCH_MARKER}`,
    "            if (workerCliPlan[i - 1] === 'codex') {",
    "                const writableRoots = [];",
    "                if (workerWorkspace.worktreeRepoRoot) {",
    "                    writableRoots.push(join(workerWorkspace.worktreeRepoRoot, '.git'));",
    "                }",
    "                writableRoots.push(teamStateRoot);",
    "                const existingAddDirTargets = new Set();",
    "                for (let argIndex = 0; argIndex < workerLaunchArgs.length - 1; argIndex += 1) {",
    "                    if (workerLaunchArgs[argIndex] === '--add-dir') {",
    "                        existingAddDirTargets.add(workerLaunchArgs[argIndex + 1]);",
    "                    }",
    "                }",
    "                for (const writableRoot of writableRoots) {",
    "                    if (typeof writableRoot !== 'string' || writableRoot.trim() === '') {",
    "                        continue;",
    "                    }",
    "                    if (existingAddDirTargets.has(writableRoot)) {",
    "                        continue;",
    "                    }",
    "                    workerLaunchArgs.push('--add-dir', writableRoot);",
    "                    existingAddDirTargets.add(writableRoot);",
    "                }",
    "            }",
    "            const resolvedWorkerModel = parseTeamWorkerLaunchArgs(workerLaunchArgs).modelOverride ?? undefined;",
  ].join("\n");
  return { changed: true, status: "patched", content: raw.replace(anchor, replacement) };
}

export async function inspectRuntime(filePath = defaultRuntimePath(), backupDir = DEFAULT_BACKUP_DIR) {
  const existsTarget = await exists(filePath);
  if (!existsTarget) {
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

export async function applyRuntimeFix(filePath = defaultRuntimePath(), backupDir = DEFAULT_BACKUP_DIR) {
  if (!(await exists(filePath))) {
    return { ok: false, targetPath: filePath, backupDir, status: "missing_target", changed: false };
  }
  const raw = await fs.readFile(filePath, "utf8");
  const patchResult = patchWorktreeWritableRoots(raw);
  if (!patchResult.changed) {
    return { ok: patchResult.status === "already_patched", targetPath: filePath, backupDir, status: patchResult.status, changed: false, patchMarker: PATCH_MARKER };
  }
  await ensureDir(backupDir);
  const backupPath = path.join(backupDir, `${path.basename(filePath)}.${nowTag()}.bak`);
  await fs.writeFile(backupPath, raw, "utf8");
  await fs.writeFile(filePath, patchResult.content, "utf8");
  return { ok: true, targetPath: filePath, backupDir, backupPath, status: patchResult.status, changed: true, patchMarker: PATCH_MARKER };
}

export async function restoreLatestBackup(filePath = defaultRuntimePath(), backupDir = DEFAULT_BACKUP_DIR) {
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
  const targetIndex = args.indexOf("--target");
  const backupIndex = args.indexOf("--backup-dir");
  const targetPath = targetIndex >= 0 && targetIndex + 1 < args.length ? path.resolve(args[targetIndex + 1]) : defaultRuntimePath();
  const backupDir = backupIndex >= 0 && backupIndex + 1 < args.length ? path.resolve(args[backupIndex + 1]) : DEFAULT_BACKUP_DIR;
  let result;
  switch (command) {
    case "status":
      result = await inspectRuntime(targetPath, backupDir);
      break;
    case "apply":
      result = await applyRuntimeFix(targetPath, backupDir);
      break;
    case "restore":
      result = await restoreLatestBackup(targetPath, backupDir);
      break;
    default:
      throw new Error(`unknown command: ${command}`);
  }
  print(result, json);
  if (result.ok === false) process.exitCode = 1;
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
