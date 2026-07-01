import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-prompt-controller-shutdown-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_SHUTDOWN_FIX_V1";

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

function replaceLineEndingAware(raw, block, replacement) {
  if (raw.includes(block)) {
    return { matched: true, content: raw.replace(block, replacement) };
  }

  const crlfBlock = block.replace(/\n/g, "\r\n");
  if (raw.includes(crlfBlock)) {
    return { matched: true, content: raw.replace(crlfBlock, replacement.replace(/\n/g, "\r\n")) };
  }

  return { matched: false, content: raw };
}

export function patchPromptControllerShutdown(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const statusBlock = `const statusPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'status.json')
        : '';
    const omxEntryPath = resolveOmxCliEntryPath();`;
  const statusPatch = replaceLineEndingAware(
    raw,
    statusBlock,
    `const statusPath = teamName && workerName && teamStateRoot
        ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'status.json')
        : '';
    // ${PATCH_MARKER}
    const childPidPath = teamName && workerName && controllerDebugRoot
        ? join(controllerDebugRoot, \`${"${"}workerName}.child-pid.json\`)
        : (teamName && workerName && teamStateRoot
            ? join(teamStateRoot, 'team', teamName, 'workers', workerName, 'child-pid.json')
            : '');
    const omxEntryPath = resolveOmxCliEntryPath();`,
  );
  if (!statusPatch.matched) {
    return { changed: false, status: "status_path_block_missing", content: raw };
  }
  let next = statusPatch.content;

  const logBlock = `const log = (event, details = {}) => {
        if (controllerLogPath === '')
            return;
        try {
            mkdirSync(dirname(controllerLogPath), { recursive: true });
        }
        catch {
            // Fall through to append attempt.
        }
        try {
            appendFileSync(controllerLogPath, \`${"${"}JSON.stringify({ ts: new Date().toISOString(), event, ...details })}\\n\`, 'utf-8');
        }
        catch {
            // Best-effort debug log only.
        }
    };`;

  const logPatch = replaceLineEndingAware(
    next,
    logBlock,
    `${logBlock}
    const writeChildPidSnapshot = (details = {}) => {
        if (childPidPath === '')
            return;
        const childPid = activeChild?.pid ?? null;
        try {
            mkdirSync(dirname(childPidPath), { recursive: true });
            writeFileSync(childPidPath, JSON.stringify({
                pid: childPid,
                child_pid: childPid,
                active: activeChild !== null && activeChild.exitCode === null,
                updated_at: new Date().toISOString(),
                ...details,
            }, null, 2), 'utf-8');
        }
        catch (error) {
            log('child_pid_snapshot_error', {
                message: error instanceof Error ? error.message : String(error),
            });
        }
    };
    const terminateActiveChild = (reason) => {
        const child = activeChild;
        if (child === null || child.exitCode !== null)
            return;
        writeChildPidSnapshot({ event: 'controller_shutdown', reason });
        try {
            child.kill('SIGTERM');
        }
        catch (error) {
            log('active_child_sigterm_error', {
                reason,
                childPid: child.pid ?? null,
                message: error instanceof Error ? error.message : String(error),
            });
        }
        setTimeout(() => {
            if (child.exitCode !== null)
                return;
            try {
                child.kill('SIGKILL');
            }
            catch (error) {
                log('active_child_sigkill_error', {
                    reason,
                    childPid: child.pid ?? null,
                    message: error instanceof Error ? error.message : String(error),
                });
            }
        }, 1000).unref?.();
    };
    const requestControllerShutdown = (signal) => {
        log('controller_shutdown_signal', { signal, activeChildPid: activeChild?.pid ?? null, queueLength: queue.length });
        terminateActiveChild(signal);
        setTimeout(() => process.exit(0), 1500).unref?.();
    };
    process.once('SIGTERM', () => requestControllerShutdown('SIGTERM'));
    process.once('SIGINT', () => requestControllerShutdown('SIGINT'));`,
  );
  if (!logPatch.matched) {
    return { changed: false, status: "log_block_missing", content: raw };
  }
  next = logPatch.content;

  const spawnBlock = `activeChild = spawn(command, args, {
                cwd: process.cwd(),
                env: process.env,
                stdio: ['pipe', stdoutFd, stderrFd],
                windowsHide: true,
            });
            // OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_STDIN_CLOSE_FIX_V1`;

  const spawnPatch = replaceLineEndingAware(
    next,
    spawnBlock,
    `activeChild = spawn(command, args, {
                cwd: process.cwd(),
                env: process.env,
                stdio: ['pipe', stdoutFd, stderrFd],
                windowsHide: true,
            });
            writeChildPidSnapshot({ event: 'launch_exec', launchMode, promptLength: normalizedPrompt.length });
            // OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_STDIN_CLOSE_FIX_V1`,
  );
  if (!spawnPatch.matched) {
    return { changed: false, status: "spawn_block_missing", content: raw };
  }
  next = spawnPatch.content;

  const exitBlock = `activeChild.once('exit', () => {
            log('exec_exit', { code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null });
            activeChild = null;`;

  const exitPatch = replaceLineEndingAware(
    next,
    exitBlock,
    `activeChild.once('exit', () => {
            log('exec_exit', { code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null });
            writeChildPidSnapshot({ event: 'exec_exit', code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null, active: false });
            activeChild = null;`,
  );
  if (!exitPatch.matched) {
    return { changed: false, status: "exit_block_missing", content: raw };
  }
  next = exitPatch.content;

  return { changed: true, status: "patched", content: next };
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
  const patchResult = patchPromptControllerShutdown(raw);
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
