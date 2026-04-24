import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-worker-bootstrap-mailbox-example-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_WORKER_BOOTSTRAP_MAILBOX_EXAMPLE_FIX_V1";

function defaultBootstrapPath() {
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

export function patchWorkerBootstrapMailboxExamples(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }
  const legacyBlock = [
    "Example:",
    `omx team api send-message --input "{\\"team_name\\":\\"${"${"}teamName}\\",\\"from_worker\\":\\"<your-worker-name>\\",\\"to_worker\\":\\"leader-fixed\\",\\"body\\":\\"ACK: <your-worker-name> initialized\\"}" --json`,
    "",
    "CRITICAL: Never omit from_worker. The MCP server cannot auto-detect your identity.",
    "",
    "When your mailbox receives a message, process delivery explicitly:",
    '1. Read: \\`omx team api mailbox-list --input "{\\"team_name\\":\\"${teamName}\\",\\"worker\\":\\"<your-worker-name>\\"}" --json\\`',
    '2. Mark delivered: \\`omx team api mailbox-mark-delivered --input "{\\"team_name\\":\\"${teamName}\\",\\"worker\\":\\"<your-worker-name>\\",\\"message_id\\":\\"<MESSAGE_ID>\\"}" --json\\`',
    "3. If you reply, include concrete progress and keep executing your assigned work or the next feasible task after replying.",
  ].join("\n");
  let matchedLegacyBlock = null;
  if (raw.includes(legacyBlock)) {
    matchedLegacyBlock = legacyBlock;
  }
  if (!matchedLegacyBlock) {
    return { changed: false, status: "legacy_block_missing", content: raw };
  }
  const ackReplacement = [
    `// ${PATCH_MARKER}`,
    `$payload = @{ team_name = "${"${"}teamName}"; from_worker = "<your-worker-name>"; to_worker = "leader-fixed"; body = "ACK: <your-worker-name> initialized" } | ConvertTo-Json -Compress`,
    "omx team api send-message --input $payload --json",
  ].join("\n");
  const mailboxReadReplacement = [
    "1. Read:",
    '   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>" } | ConvertTo-Json -Compress\\`',
    '   \\`omx team api mailbox-list --input $payload --json\\`',
  ].join("\n");
  const mailboxMarkReplacement = [
    "2. Mark delivered:",
    '   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress\\`',
    '   \\`omx team api mailbox-mark-delivered --input $payload --json\\`',
  ].join("\n");
  const replacementBlock = [
    "Example:",
    ackReplacement,
    "",
    "CRITICAL: Never omit from_worker. The MCP server cannot auto-detect your identity.",
    "",
    "When your mailbox receives a message, process delivery explicitly:",
    mailboxReadReplacement,
    mailboxMarkReplacement,
    "3. If you reply, include concrete progress and keep executing your assigned work or the next feasible task after replying.",
  ].join("\n");
  const content = raw.replace(matchedLegacyBlock, replacementBlock);
  return { changed: true, status: "patched", content };
}

export async function inspectBootstrap(filePath = defaultBootstrapPath(), backupDir = DEFAULT_BACKUP_DIR) {
  const bootstrapExists = await exists(filePath);
  if (!bootstrapExists) {
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

export async function applyBootstrapFix(filePath = defaultBootstrapPath(), backupDir = DEFAULT_BACKUP_DIR) {
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
  const patchResult = patchWorkerBootstrapMailboxExamples(raw);
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

export async function restoreLatestBackup(filePath = defaultBootstrapPath(), backupDir = DEFAULT_BACKUP_DIR) {
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
  const targetPath = targetIndex >= 0 && targetIndex + 1 < args.length ? path.resolve(args[targetIndex + 1]) : defaultBootstrapPath();
  const backupDir = backupIndex >= 0 && backupIndex + 1 < args.length ? path.resolve(args[backupIndex + 1]) : DEFAULT_BACKUP_DIR;

  let result;
  switch (command) {
    case "status":
      result = await inspectBootstrap(targetPath, backupDir);
      break;
    case "apply":
      result = await applyBootstrapFix(targetPath, backupDir);
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
