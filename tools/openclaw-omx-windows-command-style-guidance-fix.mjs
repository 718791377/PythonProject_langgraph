import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const ROOT_DIR = "D:\\PythonProject_langgraph";
const DEFAULT_BACKUP_DIR = path.join(
  ROOT_DIR,
  ".tmp",
  "backups",
  "omx-windows-command-style-guidance-fix",
);
export const PATCH_MARKER = "OPENCLAW_OMX_WINDOWS_COMMAND_STYLE_GUIDANCE_FIX_V1";

function defaultTargets() {
  const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
  return [
    path.join(appData, "npm", "node_modules", "oh-my-codex", "dist", "team", "worker-bootstrap.js"),
    path.join(os.homedir(), ".codex", "skills", "worker", "SKILL.md"),
  ];
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

export function patchCommandStyleGuidance(raw) {
  if (raw.includes(PATCH_MARKER)) {
    return { changed: false, status: "already_patched", content: raw };
  }
  const legacySentence = "use a PowerShell variable or file-backed JSON only.";
  const strongSentence = `use the direct one-line form \`omx team api ... --input (@{...} | ConvertTo-Json -Compress) --json\` only. Never create a separate \`$payload\` variable, never quote \`$payload\`, and never split the PowerShell command across lines.`;
  let content = raw;
  let changed = false;
  if (content.includes(legacySentence)) {
    content = content.replaceAll(legacySentence, `${strongSentence}\n// ${PATCH_MARKER}`);
    changed = true;
  }
  const workerSkillNeedle = "Windows PowerShell:\n\n```powershell";
  const workerSkillInsert = `${workerSkillNeedle}\n# ${PATCH_MARKER}\n# On Windows, use the direct one-line --input (@{...} | ConvertTo-Json -Compress) form for ALL omx team api calls.\n# Never create a separate $payload variable inside a model-generated exec command.\n`;
  if (content.includes(workerSkillNeedle) && !content.includes(`# ${PATCH_MARKER}\n# On Windows, use the direct one-line`)) {
    content = content.replace(workerSkillNeedle, workerSkillInsert);
    changed = true;
  }
  return { changed, status: changed ? "patched" : "no_known_guidance_anchor", content };
}

async function applyOne(filePath, backupDir) {
  if (!(await exists(filePath))) {
    return { ok: false, targetPath: filePath, backupDir, status: "missing_target", changed: false };
  }
  const raw = await fs.readFile(filePath, "utf8");
  const patchResult = patchCommandStyleGuidance(raw);
  if (!patchResult.changed) {
    return { ok: patchResult.status === "already_patched", targetPath: filePath, backupDir, status: patchResult.status, changed: false, patchMarker: PATCH_MARKER };
  }
  await ensureDir(backupDir);
  const backupPath = path.join(backupDir, `${path.basename(filePath)}.${nowTag()}.bak`);
  await fs.writeFile(backupPath, raw, "utf8");
  await fs.writeFile(filePath, patchResult.content, "utf8");
  return { ok: true, targetPath: filePath, backupDir, backupPath, status: patchResult.status, changed: true, patchMarker: PATCH_MARKER };
}

async function inspectOne(filePath, backupDir) {
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
  const targets = defaultTargets();
  const results = [];
  for (const target of targets) {
    const backupDir = path.join(DEFAULT_BACKUP_DIR, path.basename(target));
    if (command === "status") results.push(await inspectOne(target, backupDir));
    else if (command === "apply") results.push(await applyOne(target, backupDir));
    else if (command === "restore") results.push(await restoreOne(target, backupDir));
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
