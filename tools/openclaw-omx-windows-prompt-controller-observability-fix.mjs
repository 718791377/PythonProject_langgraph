import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-prompt-controller-observability-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_OBSERVABILITY_FIX_V1";

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

export function patchPromptControllerObservability(raw) {
  const hasMarker = raw.includes(PATCH_MARKER);
  const fsImportPattern = /import \{ existsSync, appendFileSync, mkdirSync \} from 'fs';/m;
  const fsImportPatchedPattern = /import \{ existsSync, appendFileSync, mkdirSync, openSync, closeSync \} from 'fs';/m;
  const spawnBlockPattern =
    /const controllerPath = join\(dirname\(omxEntryPath\), '\.\.', 'team', 'windows-worker-controller\.js'\);[\s\S]*?registerPromptWorkerHandle\(teamName, workerName, controllerChild, controllerPid\);\s*return \{ child: controllerChild, pid: controllerPid \};|const controllerPath = join\(dirname\(omxEntryPath\), '\.\.', 'team', 'windows-worker-controller\.js'\);[\s\S]*?registerPromptWorkerHandle\(teamName, workerName, null, controllerPid\);\s*return \{ child: null, pid: controllerPid \};/m;
  const hasStableDebugRoot = /const controllerDebugRoot = join\(teamStateRoot, 'prompt-controller-debug', teamName\);/.test(raw)
    && /resolveCanonicalTeamStateRoot\(workerCwd, \{ \.\.\.process\.env, \.\.\.processSpec\.env, \.\.\.workerEnv \}\);/.test(raw)
    && /OMX_WINDOWS_PROMPT_CONTROLLER_DEBUG_ROOT: controllerDebugRoot,/.test(raw);
  if (!fsImportPattern.test(raw) && !fsImportPatchedPattern.test(raw)) {
    return { changed: false, status: "fs_import_missing", content: raw };
  }
  if (!spawnBlockPattern.test(raw)) {
    return { changed: false, status: "spawn_block_missing", content: raw };
  }
  const updatedImport = fsImportPattern.test(raw)
    ? raw.replace(
        fsImportPattern,
        "import { existsSync, appendFileSync, mkdirSync, openSync, closeSync } from 'fs';",
      )
    : raw;
  if (hasMarker && hasStableDebugRoot) {
    return { changed: false, status: "already_patched", content: updatedImport };
  }
  const replacement = [
    `const controllerPath = join(dirname(omxEntryPath), '..', 'team', 'windows-worker-controller.js');`,
    `        const teamStateRoot = resolveCanonicalTeamStateRoot(workerCwd, { ...process.env, ...processSpec.env, ...workerEnv });`,
    `        const controllerDebugRoot = join(teamStateRoot, 'prompt-controller-debug', teamName);`,
    `        const controllerLogPath = join(controllerDebugRoot, \`${"${"}workerName}.bootstrap.log\`);`,
    `        const controllerStdoutLogPath = join(controllerDebugRoot, \`${"${"}workerName}.stdout.log\`);`,
    `        const controllerStderrLogPath = join(controllerDebugRoot, \`${"${"}workerName}.stderr.log\`);`,
    `        const appendControllerBootstrapLog = (event, details = {}) => {`,
    `            try {`,
    `                mkdirSync(controllerDebugRoot, { recursive: true });`,
    `                appendFileSync(controllerLogPath, \`${"${"}JSON.stringify({ ts: new Date().toISOString(), event, ...details })}\\n\`, 'utf-8');`,
    `            }`,
    `            catch {`,
    `                // Best-effort bootstrap log only.`,
    `            }`,
    `        };`,
    `        const launchEnv = {`,
    `            ...process.env,`,
    `            ...processSpec.env,`,
    `            ...workerEnv,`,
    `            [TEAM_WORKER_ENV]: \`${"${"}teamName}/${"${"}workerName}\`,`,
    `            OMX_WINDOWS_PROMPT_WORKER_LAUNCH_ARGS_JSON: JSON.stringify(launchArgs),`,
    `            OMX_WINDOWS_PROMPT_WORKER_INITIAL_PROMPT: initialPrompt ?? '',`,
    `            OMX_WINDOWS_PROMPT_WORKER_ROLE: workerRole ?? '',`,
    `            OMX_WINDOWS_PROMPT_CONTROLLER_DEBUG_ROOT: controllerDebugRoot,`,
    `        };`,
    `        mkdirSync(controllerDebugRoot, { recursive: true });`,
    `        const controllerStdoutFd = openSync(controllerStdoutLogPath, 'a');`,
    `        const controllerStderrFd = openSync(controllerStderrLogPath, 'a');`,
    `        let controllerChild;`,
    `        try {`,
    `            // ${PATCH_MARKER}`,
    `            controllerChild = spawn(process.execPath, [controllerPath], {`,
    `                cwd: workerCwd,`,
    `                env: launchEnv,`,
    `                stdio: ['ignore', controllerStdoutFd, controllerStderrFd],`,
    `                windowsHide: true,`,
    `            });`,
    `        }`,
    `        finally {`,
    `            try {`,
    `                closeSync(controllerStdoutFd);`,
    `            }`,
    `            catch {`,
    `                // Best-effort descriptor cleanup only.`,
    `            }`,
    `            try {`,
    `                closeSync(controllerStderrFd);`,
    `            }`,
    `            catch {`,
    `                // Best-effort descriptor cleanup only.`,
    `            }`,
    `        }`,
    `        controllerChild.once('error', (error) => {`,
    `            appendControllerBootstrapLog('controller_bootstrap_error', {`,
    `                message: error instanceof Error ? error.message : String(error),`,
    `            });`,
    `        });`,
    `        controllerChild.once('exit', (code, signal) => {`,
    `            appendControllerBootstrapLog('controller_bootstrap_exit', { code, signal });`,
    `        });`,
    `        if (controllerChild.error) {`,
    `            throw controllerChild.error;`,
    `        }`,
    `        const controllerPid = controllerChild.pid ?? 0;`,
    `        if (!Number.isFinite(controllerPid) || controllerPid <= 0) {`,
    `            throw new Error('windows_prompt_controller_bootstrap_missing_pid');`,
    `        }`,
    `        appendControllerBootstrapLog('controller_bootstrap_spawned', {`,
    `            pid: controllerPid,`,
    `            controllerPath,`,
    `            controllerStdoutLogPath,`,
    `            controllerStderrLogPath,`,
    `        });`,
    `        controllerChild.unref();`,
    `        registerPromptWorkerHandle(teamName, workerName, controllerChild, controllerPid);`,
    `        return { child: controllerChild, pid: controllerPid };`,
  ].join("\n");
  return {
    changed: true,
    status: hasMarker ? "normalized_legacy_patch" : "patched",
    content: updatedImport.replace(spawnBlockPattern, replacement),
  };
}

export async function inspectRuntime(filePath = defaultRuntimePath(), backupDir = DEFAULT_BACKUP_DIR) {
  const runtimeExists = await exists(filePath);
  if (!runtimeExists) {
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

export async function applyRuntimeFix(filePath = defaultRuntimePath(), backupDir = DEFAULT_BACKUP_DIR) {
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
  const patchResult = patchPromptControllerObservability(raw);
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

export async function restoreLatestBackup(filePath = defaultRuntimePath(), backupDir = DEFAULT_BACKUP_DIR) {
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
