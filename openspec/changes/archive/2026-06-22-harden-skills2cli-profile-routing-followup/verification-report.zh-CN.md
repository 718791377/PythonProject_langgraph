# 验证报告：硬化 Skills2CLI Profile Routing 后续契约

## 范围

Stage B 在本地实现已冻结的 Skills2CLI profile routing hardening package。验证范围不包含 profile apply、`config.toml` 修改、plugin cache 编辑、vendor `SKILL.md` 编辑、GitLab push、GitLab MR 或 GitHub sync。

## 新鲜验证证据

- `python test\skills2cli.test.py` - 通过，16 tests。
- `python test\check_skills2cli_profile_routing.test.py` - 通过，8 tests。
- `python test\check_plugin_modules_skill.test.py` - 通过，15 tests。
- `python -X utf8 tools\check_plugin_modules_skill.py --root . --json` - 通过，`ok=true`，`errors=0`。
- `python -X utf8 tools\check_skills2cli_profile_routing.py --root . --json` - 通过，`ok=true`，`errors=0`；预期 warning 报告 installed user-level drift。
- 代表性 `skills2cli profile suggest` smokes 显示 GitLab CI/security、Expo/Sentry、Twilio WhatsApp 的 focused top profile recommendation；只有显式 all-plugin troubleshooting 才选择 `full`。
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools\skill_sources\plugin-modules\scripts\load_module.ps1 web-saas.mobile-app -Json` - 输出 soft-load task-module guidance，且无 mutation flags。
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools\skill_sources\plugin-modules\scripts\set_plugin_profile.ps1 web-saas.mobile-app -Json` - 拒绝 nested hard-load，并给出 preview/soft-load guidance，且无 mutation flags。
- `openspec validate harden-skills2cli-profile-routing-followup --strict` - 通过。
- `python tools\run_openspec_guard.py --root . --tool codex --json` - 通过，`77/77` steps。
- `python tools\check_precommit_update_archive.py --root . --json` - 通过，`ok=true`。

## 验收映射

- Scenario-based profile routing metadata：由 registry fields 和 `check_skills2cli_profile_routing.py` / `check_plugin_modules_skill.py` 覆盖。
- Task-module identity：由 `qualified_name` 与 missing/wrong identity focused tests 覆盖。
- Hard-load top-level only：由 `set_plugin_profile.ps1` nested rejection smoke 覆盖。
- Advisory suggestion：由 `skills2cli.py profile suggest` mutation flags 与测试覆盖。
- Known plugin non-full coverage：checker 报告 `known_plugins=37` 与 `non_full_plugin_coverage=37`。
- Shared contract：`skills2cli_profile_registry_contract.py` 集中 schema、path、accessor 与 installed artifact surfaces。
- Explicit `full`：普通 query 排除 `full`；显式 all-plugin troubleshooting 使用 `why_full_selected` 选择 `full`。
- UTF-8 stable checker JSON：checker matrix 包含中文 full troubleshooting row，且 JSON 可解码。
- Installed artifact drift：checker 报告 `skills2cli.py`、`skills2cli_profile_registry_contract.py` 与 `profiles.json` drift surfaces。

## 决策

local gate 与 local MR review 通过后，继续归档并集成本地 `main`。停止在 remote-publication approval gate。
