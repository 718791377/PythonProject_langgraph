import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-prompt-controller-debug-root-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_DEBUG_ROOT_FIX_V1";

function defaultControllerPath() {
  const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
  return path.join(
    appData,
    "npm",
    "node_modules",
    "oh-my-codex",
    "dist",
    "team",
    "windows-worker-controller.js",
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

export function patchPromptControllerDebugRoot(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }
  const pathBlockPattern =
    /const inboxPath = teamName && workerName && teamStateRoot\s*\? join\(teamStateRoot, 'team', teamName, 'workers', workerName, 'inbox\.md'\)\s*: '';\s*const controllerLogPath = teamName && workerName && teamStateRoot\s*\? join\(teamStateRoot, 'team', teamName, 'workers', workerName, 'controller\.log'\)\s*: '';\s*const execStdoutLogPath = teamName && workerName && teamStateRoot\s*\? join\(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec\.stdout\.log'\)\s*: '';\s*const execStderrLogPath = teamName && workerName && teamStateRoot\s*\? join\(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec\.stderr\.log'\)\s*: '';/m;
  if (!pathBlockPattern.test(raw)) {
    return { changed: false, status: "path_block_missing", content: raw };
  }
  const replacement = [
    `const controllerDebugRoot = String(process.env.OMX_WINDOWS_PROMPT_CONTROLLER_DEBUG_ROOT ?? '').trim();`,
    `    const inboxPath = teamName && workerName && teamStateRoot`,
    `        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'inbox.md')`,
    `        : '';`,
    `    // ${PATCH_MARKER}`,
    `    const controllerLogPath = teamName && workerName && controllerDebugRoot`,
    `        ? join(controllerDebugRoot, \`${"${"}workerName}.controller.log\`)`,
    `        : (teamName && workerName && teamStateRoot`,
    `            ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'controller.log')`,
    `            : '');`,
    `    const execStdoutLogPath = teamName && workerName && controllerDebugRoot`,
    `        ? join(controllerDebugRoot, \`${"${"}workerName}.exec.stdout.log\`)`,
    `        : (teamName && workerName && teamStateRoot`,
    `            ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec.stdout.log')`,
    `            : '');`,
    `    const execStderrLogPath = teamName && workerName && controllerDebugRoot`,
    `        ? join(controllerDebugRoot, \`${"${"}workerName}.exec.stderr.log\`)`,
    `        : (teamName && workerName && teamStateRoot`,
    `            ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'exec.stderr.log')`,
    `            : '');`,
  ].join("\n");
  return { changed: true, status: "patched", content: raw.replace(pathBlockPattern, replacement) };
}

export async function inspectController(filePath = defaultControllerPath(), backupDir = DEFAULT_BACKUP_DIR) {
  const controllerExists = await exists(filePath);
  if (!controllerExists) {
    return {
      ok: false,
      targetPath: filePath,
      backupDir,
      exists: false,
      patched: false,
      backupCount: 0,
      patchMarker: PATCH_MARKER,
    };
  }
  const raw = await fs.readFile(filePath, "utf8");
  let backupCount = 0;
  if (await exists(backupDir)) {
    const entries = await fs.readdir(backupDir, { withFileTypes: true });
    const basename = path.basename(filePath);
    backupCount = entries.filter(
      (entry) => entry.isFile() && entry.name.startsWith(`${basename}.`) && entry.name.endsWith(".bak"),
    ).length;
  }
  return {
    ok: true,
    targetPath: filePath,
    backupDir,
    exists: true,
    patched: raw.includes(PATCH_MARKER),
    patchMarker: PATCH_MARKER,
    backupCount,
  };
}

export async function applyControllerFix(filePath = defaultControllerPath(), backupDir = DEFAULT_BACKUP_DIR) {
  if (!(await exists(filePath))) {
    return {
      ok: false,
      targetPath: filePath,
      backupDir,
      status: "missing_target",
      changed: false,
    };
  }
  const raw = await fs.readFile(filePath, "utf8");
  const patchResult = patchPromptControllerDebugRoot(raw);
  if (!patchResult.changed) {
    return {
      ok: patchResult.status === "already_patched",
      targetPath: filePath,
      backupDir,
      status: patchResult.status,
      changed: false,
      patchMarker: PATCH_MARKER,
    };
  }
  await ensureDir(backupDir);
  const backupPath = path.join(backupDir, `${path.basename(filePath)}.${nowTag()}.bak`);
  await fs.writeFile(backupPath, raw, "utf8");
  await fs.writeFile(filePath, patchResult.content, "utf8");
  return {
    ok: true,
    targetPath: filePath,
    backupDir,
    backupPath,
    status: patchResult.status,
    changed: true,
    patchMarker: PATCH_MARKER,
  };
}

export async function restoreLatestBackup(filePath = defaultControllerPath(), backupDir = DEFAULT_BACKUP_DIR) {
  if (!(await exists(backupDir))) {
    return {
      ok: false,
      targetPath: filePath,
      backupDir,
      status: "backup_missing",
      changed: false,
    };
  }
  const basename = path.basename(filePath);
  const entries = await fs.readdir(backupDir, { withFileTypes: true });
  const candidates = entries
    .filter((entry) => entry.isFile() && entry.name.startsWith(`${basename}.`) && entry.name.endsWith(".bak"))
    .map((entry) => path.join(backupDir, entry.name))
    .sort();
  const latestBackup = candidates.at(-1);
  if (!latestBackup) {
    return {
      ok: false,
      targetPath: filePath,
      backupDir,
      status: "backup_missing",
      changed: false,
    };
  }
  const backupRaw = await fs.readFile(latestBackup, "utf8");
  await fs.writeFile(filePath, backupRaw, "utf8");
  return {
    ok: true,
    targetPath: filePath,
    backupDir,
    backupPath: latestBackup,
    status: "restored",
    changed: true,
  };
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
  const targetPath = targetIndex >= 0 && targetIndex + 1 < args.length ? path.resolve(args[targetIndex + 1]) : defaultControllerPath();
  const backupDir = backupIndex >= 0 && backupIndex + 1 < args.length ? path.resolve(args[backupIndex + 1]) : DEFAULT_BACKUP_DIR;

  let result;
  switch (command) {
    case "status":
      result = await inspectController(targetPath, backupDir);
      break;
    case "apply":
      result = await applyControllerFix(targetPath, backupDir);
      break;
    case "restore":
      result = await restoreLatestBackup(targetPath, backupDir);
      break;
    default:
      throw new Error(`unknown command: ${command}`);
  }
  print(result, json);
  if (result.ok === false) {
    process.exitCode = 1;
  }
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
