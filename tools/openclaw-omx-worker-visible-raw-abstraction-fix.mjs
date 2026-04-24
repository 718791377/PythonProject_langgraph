import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-worker-visible-raw-abstraction-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WORKER_VISIBLE_RAW_ABSTRACTION_FIX_V1";

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

export function patchWorkerBootstrap(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const rawSendLine = '    return `omx team api send-message --input "{\\\\"team_name\\\\":\\\\"${teamName}\\\\",\\\\"from_worker\\\\":\\\\"${workerName}\\\\",\\\\"to_worker\\\\":\\\\"leader-fixed\\\\",\\\\"body\\\\":\\\\"ACK: ${workerName} initialized\\\\"}" --json`;';
  const rawListLine = '    return `omx team api mailbox-list --input "{\\\\"team_name\\\\":\\\\"${teamName}\\\\",\\\\"worker\\\\":\\\\"${workerName}\\\\"}" --json`;';
  const rawDeliveredLine = '    return `omx team api mailbox-mark-delivered --input "{\\\\"team_name\\\\":\\\\"${teamName}\\\\",\\\\"worker\\\\":\\\\"${workerName}\\\\",\\\\"message_id\\\\":\\\\"<MESSAGE_ID>\\\\"}" --json`;';
  const helperAnchor = 'function buildWorkerRootAgentsBackupPath(teamStateRoot, teamName, workerName, worktreePath) {';
  const overlayAckRaw = [
    'Example:',
    '// OPENCLAW_OMX_WINDOWS_WORKER_BOOTSTRAP_MAILBOX_EXAMPLE_FIX_V1',
    '$payload = @{ team_name = "${teamName}"; from_worker = "<your-worker-name>"; to_worker = "leader-fixed"; body = "ACK: <your-worker-name> initialized" } | ConvertTo-Json -Compress',
    'omx team api send-message --input $payload --json',
  ].join("\n");
  const overlayMailboxRaw = [
    '1. Read:',
    '   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>" } | ConvertTo-Json -Compress\\`',
    '   \\`omx team api mailbox-list --input $payload --json\\`',
    '2. Mark delivered:',
    '   \\`$payload = @{ team_name = "${teamName}"; worker = "<your-worker-name>"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress\\`',
    '   \\`omx team api mailbox-mark-delivered --input $payload --json\\`',
  ].join("\n");

  if (!raw.includes(rawSendLine) || !raw.includes(rawListLine) || !raw.includes(rawDeliveredLine) || !raw.includes(helperAnchor)) {
    return { changed: false, status: "expected_bootstrap_shape_missing", content: raw };
  }

  let content = raw
    .replace(rawSendLine, '    return buildRawTeamApiExample("send-message", { team_name: teamName, from_worker: workerName, to_worker: "leader-fixed", body: `ACK: ${workerName} initialized` });')
    .replace(rawListLine, '    return buildRawTeamApiExample("mailbox-list", { team_name: teamName, worker: workerName });')
    .replace(rawDeliveredLine, '    return buildRawTeamApiExample("mailbox-mark-delivered", { team_name: teamName, worker: workerName, message_id: "<MESSAGE_ID>" });');

  const helperBlock = [
    `// ${PATCH_MARKER}`,
    "function buildRawTeamApiPayload(payload) {",
    "    return JSON.stringify(payload).replaceAll('\\\\', '\\\\\\\\').replaceAll('\"', '\\\\\"');",
    "}",
    "function buildRawTeamApiExample(operation, payload) {",
    "    return `omx team api ${operation} --input \"${buildRawTeamApiPayload(payload)}\" --json`;",
    "}",
    "",
  ].join("\n");
  content = content.replace(helperAnchor, `${helperBlock}${helperAnchor}`);

  if (content.includes(overlayAckRaw)) {
    content = content.replace(
      overlayAckRaw,
      [
        "Example:",
        "omx-team-send-message.ps1 -TeamName \"${teamName}\" -FromWorker \"<your-worker-name>\" -ToWorker \"leader-fixed\" -Body \"ACK: <your-worker-name> initialized\" -Json",
      ].join("\n"),
    );
  }

  if (content.includes(overlayMailboxRaw)) {
    content = content.replace(
      overlayMailboxRaw,
      [
        "1. Read:",
        "   \\`omx-team-mailbox-list.ps1 -TeamName \"${teamName}\" -Worker \"<your-worker-name>\" -Json\\`",
        "2. Mark delivered:",
        "   \\`omx-team-mailbox-mark-delivered.ps1 -TeamName \"${teamName}\" -Worker \"<your-worker-name>\" -MessageId \"<MESSAGE_ID>\" -Json\\`",
      ].join("\n"),
    );
  }

  return { changed: true, status: "patched", content };
}

export function patchWorkerSkill(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const rawSendBlock = [
    "Copy/paste template:",
    "",
    "```bash",
    'omx team api send-message --input "{\\"team_name\\":\\"<teamName>\\",\\"from_worker\\":\\"<workerName>\\",\\"to_worker\\":\\"leader-fixed\\",\\"body\\":\\"ACK: <workerName> initialized\\"}" --json',
    "```",
  ].join("\n");
  const rawMailboxBlock = [
    "Use CLI interop:",
    "- `omx team api mailbox-list --json` to read",
    "- `omx team api mailbox-mark-delivered --json` to acknowledge delivery",
    "",
    "Copy/paste templates:",
    "",
    "```bash",
    'omx team api mailbox-list --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\"}" --json',
    'omx team api mailbox-mark-delivered --input "{\\"team_name\\":\\"<teamName>\\",\\"worker\\":\\"<workerName>\\",\\"message_id\\":\\"<MESSAGE_ID>\\"}" --json',
    "```",
  ].join("\n");

  let content = raw;
  let changed = false;

  if (content.includes(rawSendBlock)) {
    content = content.replace(
      rawSendBlock,
      [
        `<!-- ${PATCH_MARKER}: non-Windows raw example intentionally hidden from Windows worker-visible guidance -->`,
        "Windows durable-worker wrapper:",
        "",
        "```powershell",
        'omx-team-send-message.ps1 -TeamName "<teamName>" -FromWorker "<workerName>" -ToWorker "leader-fixed" -Body "ACK: <workerName> initialized" -Json',
        "```",
        "",
        "Non-Windows fallback uses direct `omx team api send-message --input <json> --json`; raw JSON example intentionally omitted here.",
      ].join("\n"),
    );
    changed = true;
  }

  if (content.includes(rawMailboxBlock)) {
    content = content.replace(
      rawMailboxBlock,
      [
        `<!-- ${PATCH_MARKER}: non-Windows raw mailbox examples intentionally hidden from Windows worker-visible guidance -->`,
        "Windows durable-worker wrappers:",
        '- `omx-team-mailbox-list.ps1 -TeamName "<teamName>" -Worker "<workerName>" -Json`',
        '- `omx-team-mailbox-mark-delivered.ps1 -TeamName "<teamName>" -Worker "<workerName>" -MessageId "<MESSAGE_ID>" -Json`',
        "",
        "Non-Windows fallback uses direct `omx team api mailbox-list --input <json> --json` and `omx team api mailbox-mark-delivered --input <json> --json`; raw JSON examples intentionally omitted here.",
      ].join("\n"),
    );
    changed = true;
  }

  return { changed, status: changed ? "patched" : "no_known_skill_anchor", content };
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
    { path: defaultWorkerBootstrapPath(), patchFn: patchWorkerBootstrap },
    { path: defaultWorkerSkillPath(), patchFn: patchWorkerSkill },
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
