import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-prompt-runtime-shutdown-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_PROMPT_RUNTIME_SHUTDOWN_FIX_V1";

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

function ensureReadFileSyncImport(raw) {
  if (/import \{[^}]*\breadFileSync\b[^}]*\} from 'fs';/.test(raw)) {
    return raw;
  }
  return raw.replace(
    /import \{ ([^}]*) \} from 'fs';/,
    (_match, members) => `import { ${members}, readFileSync } from 'fs';`,
  );
}

export function patchPromptRuntimeShutdown(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  let next = ensureReadFileSyncImport(raw);
  if (next === raw && !/\breadFileSync\b/.test(raw)) {
    return { changed: false, status: "fs_import_missing", content: raw };
  }

  const helperAnchor = "async function terminateTrackedProcessTree(rootPid, processGroupId = null, graceMs = PROMPT_WORKER_SIGTERM_WAIT_MS, killWaitMs = PROMPT_WORKER_SIGKILL_WAIT_MS) {";
  if (!next.includes(helperAnchor)) {
    return { changed: false, status: "terminate_function_missing", content: raw };
  }

  const helperBlock = `function collectWindowsPromptControllerDiagnosticPids(teamName, workerName, cwd) {
    if (process.platform !== 'win32')
        return [];
    const stateRoot = resolveCanonicalTeamStateRoot(cwd, process.env);
    const candidates = [
        join(stateRoot, 'prompt-controller-debug', teamName, \`${"${"}workerName}.child-pid.json\`),
        join(stateRoot, 'team', teamName, 'workers', workerName, 'child-pid.json'),
    ];
    const pids = [];
    for (const candidatePath of candidates) {
        try {
            if (!existsSync(candidatePath))
                continue;
            const parsed = JSON.parse(readFileSync(candidatePath, 'utf-8'));
            const rawValues = Array.isArray(parsed?.pids)
                ? parsed.pids
                : [parsed?.pid, parsed?.child_pid, parsed?.active_child_pid];
            for (const value of rawValues) {
                const pid = typeof value === 'number' ? value : Number.parseInt(String(value ?? ''), 10);
                if (Number.isFinite(pid) && pid > 0)
                    pids.push(pid);
            }
        }
        catch {
            // Best-effort shutdown diagnostics only.
        }
    }
    return [...new Set(pids)];
}
// ${PATCH_MARKER}
`;
  const patchedTerminateSignature = "async function terminateTrackedProcessTree(rootPid, processGroupId = null, graceMs = PROMPT_WORKER_SIGTERM_WAIT_MS, killWaitMs = PROMPT_WORKER_SIGKILL_WAIT_MS, extraTrackedPids = []) {";
  next = next.replace(helperAnchor, `${helperBlock}${patchedTerminateSignature}`);

  const windowsBlock = `if (process.platform === 'win32') {
        const trackedPids = Number.isFinite(rootPid) && rootPid > 0 ? [rootPid] : [];
        if (trackedPids.length === 0) {
            return { terminated: true, forcedKill: false, trackedPids: [] };
        }
        const taskkill = spawnSync('taskkill', ['/PID', String(rootPid), '/T', '/F'], {
            stdio: 'ignore',
            windowsHide: true,
        });
        if (taskkill.error && taskkill.error.code !== 'ESRCH') {
            process.stderr.write(\`[team/runtime] operation failed: ${"${"}taskkill.error}\\n\`);
        }
        return {
            terminated: await waitForTrackedPidsExit(trackedPids, killWaitMs),
            forcedKill: true,
            trackedPids,
        };
    }`;
  const windowsReplacement = `if (process.platform === 'win32') {
        const trackedPids = [...new Set([
            ...(Number.isFinite(rootPid) && rootPid > 0 ? [rootPid] : []),
            ...extraTrackedPids,
        ].filter((pid) => Number.isFinite(pid) && pid > 0))];
        if (trackedPids.length === 0) {
            return { terminated: true, forcedKill: false, trackedPids: [] };
        }
        for (const targetPid of trackedPids) {
            const taskkill = spawnSync('taskkill', ['/PID', String(targetPid), '/T', '/F'], {
                stdio: 'ignore',
                windowsHide: true,
            });
            if (taskkill.error && taskkill.error.code !== 'ESRCH') {
                process.stderr.write(\`[team/runtime] operation failed: ${"${"}taskkill.error}\\n\`);
            }
        }
        if (await waitForTrackedPidsExit(trackedPids, killWaitMs)) {
            return { terminated: true, forcedKill: true, trackedPids };
        }
        for (const targetPid of trackedPids) {
            if (!isPidAlive(targetPid))
                continue;
            try {
                process.kill(targetPid, 'SIGTERM');
            }
            catch (err) {
                if (err.code !== 'ESRCH') {
                    process.stderr.write(\`[team/runtime] operation failed: ${"${"}err}\\n\`);
                }
            }
        }
        if (await waitForTrackedPidsExit(trackedPids, killWaitMs)) {
            return { terminated: true, forcedKill: true, trackedPids };
        }
        for (const targetPid of trackedPids) {
            if (!isPidAlive(targetPid))
                continue;
            try {
                process.kill(targetPid, 'SIGKILL');
            }
            catch (err) {
                if (err.code !== 'ESRCH') {
                    process.stderr.write(\`[team/runtime] operation failed: ${"${"}err}\\n\`);
                }
            }
        }
        return {
            terminated: await waitForTrackedPidsExit(trackedPids, killWaitMs),
            forcedKill: true,
            trackedPids,
        };
    }`;
  const windowsBlockCrlf = windowsBlock.replace(/\n/g, "\r\n");
  if (next.includes(windowsBlock)) {
    next = next.replace(windowsBlock, windowsReplacement);
  } else if (next.includes(windowsBlockCrlf)) {
    next = next.replace(windowsBlockCrlf, windowsReplacement.replace(/\n/g, "\r\n"));
  } else {
    return { changed: false, status: "windows_taskkill_block_missing", content: raw };
  }

  const teardownCall = "const teardown = await terminateTrackedProcessTree(pid ?? 0, processGroupId);";
  if (!next.includes(teardownCall)) {
    return { changed: false, status: "teardown_call_missing", content: raw };
  }
  next = next.replace(
    teardownCall,
    [
      "const extraTrackedPids = process.platform === 'win32'",
      "        ? collectWindowsPromptControllerDiagnosticPids(teamName, workerName, cwd)",
      "        : [];",
      "    const teardown = await terminateTrackedProcessTree(pid ?? 0, processGroupId, PROMPT_WORKER_SIGTERM_WAIT_MS, PROMPT_WORKER_SIGKILL_WAIT_MS, extraTrackedPids);",
    ].join("\n    "),
  );

  return { changed: true, status: "patched", content: next };
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
  const patchResult = patchPromptRuntimeShutdown(raw);
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
