import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-worker-wrapper-guidance-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_WORKER_WRAPPER_GUIDANCE_FIX_V1";

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

  const sendPattern =
    /return `omx team api send-message --input \(@\{ team_name = "\$\{teamName\}"; from_worker = "\$\{workerName\}"; to_worker = "leader-fixed"; body = "ACK: \$\{workerName\} initialized" \} \| ConvertTo-Json -Compress\) --json`;/m;
  const mailboxListPattern =
    /return `omx team api mailbox-list --input \(@\{ team_name = "\$\{teamName\}"; worker = "\$\{workerName\}" \} \| ConvertTo-Json -Compress\) --json`;/m;
  const mailboxDeliveredPattern =
    /return `omx team api mailbox-mark-delivered --input \(@\{ team_name = "\$\{teamName\}"; worker = "\$\{workerName\}"; message_id = "<MESSAGE_ID>" \} \| ConvertTo-Json -Compress\) --json`;/m;
  const windowsSentence =
    "5. On native Windows, do **not** wrap `omx team api` commands inside `cmd /c`, and do **not** inline raw JSON directly into `--input`; use a PowerShell variable or file-backed JSON only.";

  if (!sendPattern.test(raw) || !mailboxListPattern.test(raw) || !mailboxDeliveredPattern.test(raw)) {
    return { changed: false, status: "helper_pattern_missing", content: raw };
  }

  let content = raw
    .replace(
      sendPattern,
      `// ${PATCH_MARKER}\n        return \`omx-team-send-message.ps1 -TeamName "\${teamName}" -FromWorker "\${workerName}" -ToWorker "leader-fixed" -Body "ACK: \${workerName} initialized" -Json\`;`,
    )
    .replace(
      mailboxListPattern,
      `return \`omx-team-mailbox-list.ps1 -TeamName "\${teamName}" -Worker "\${workerName}" -Json\`;`,
    )
    .replace(
      mailboxDeliveredPattern,
      `return \`omx-team-mailbox-mark-delivered.ps1 -TeamName "\${teamName}" -Worker "\${workerName}" -MessageId "<MESSAGE_ID>" -Json\`;`,
    );

  if (content.includes(windowsSentence)) {
    content = content.replace(
      windowsSentence,
      "5. On native Windows durable workers, prefer the generated `omx-team-*.ps1` wrapper scripts over direct `omx team api --input ...` commands. Do **not** wrap them in `cmd /c`, do not build a separate `$payload` variable, and do not hand-write `--input` JSON.",
    );
  }

  return { changed: true, status: "patched", content };
}

export function patchWorkerSkill(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }

  const sendBlock = [
    "Windows PowerShell:",
    "",
    "```powershell",
    "# OPENCLAW_OMX_WORKER_SKILL_POWERSHELL_ONELINER_FIX_V1",
    'omx team api send-message --input (@{ team_name = "<teamName>"; from_worker = "<workerName>"; to_worker = "leader-fixed"; body = "ACK: <workerName> initialized" } | ConvertTo-Json -Compress) --json',
    "```",
  ].join("\n");
  const mailboxBlock = [
    "Windows PowerShell:",
    "",
    "```powershell",
    'omx team api mailbox-list --input (@{ team_name = "<teamName>"; worker = "<workerName>" } | ConvertTo-Json -Compress) --json',
    'omx team api mailbox-mark-delivered --input (@{ team_name = "<teamName>"; worker = "<workerName>"; message_id = "<MESSAGE_ID>" } | ConvertTo-Json -Compress) --json',
    "```",
  ].join("\n");

  if (!raw.includes(sendBlock) || !raw.includes(mailboxBlock)) {
    return { changed: false, status: "skill_pattern_missing", content: raw };
  }

  let content = raw
    .replace(
      sendBlock,
      [
        "Windows PowerShell:",
        "",
        "```powershell",
        `# ${PATCH_MARKER}`,
        'omx-team-send-message.ps1 -TeamName "<teamName>" -FromWorker "<workerName>" -ToWorker "leader-fixed" -Body "ACK: <workerName> initialized" -Json',
        "```",
      ].join("\n"),
    )
    .replace(
      mailboxBlock,
      [
        "Windows PowerShell:",
        "",
        "```powershell",
        'omx-team-mailbox-list.ps1 -TeamName "<teamName>" -Worker "<workerName>" -Json',
        'omx-team-mailbox-mark-delivered.ps1 -TeamName "<teamName>" -Worker "<workerName>" -MessageId "<MESSAGE_ID>" -Json',
        "```",
      ].join("\n"),
    );

  const policyNeedle = "- `omx team api send-message --input <json> --json` with `{team_name, from_worker, to_worker:\"leader-fixed\", body}`";
  if (content.includes(policyNeedle)) {
    content = content.replace(
      policyNeedle,
      "- On Windows, prefer the generated `omx-team-send-message.ps1` / `omx-team-mailbox-list.ps1` / `omx-team-mailbox-mark-delivered.ps1` wrapper scripts instead of hand-writing `omx team api --input ...` payloads.",
    );
  }

  return { changed: true, status: "patched", content };
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
