## 1. OpenSpec Artifacts

- [x] 1.1 创建 `implement-codex-user-level-team-mode-p5-automatic-team-routing` 的 proposal、design 与 capability specs。
- [x] 1.2 记录 automatic durable-team routing 规则、tracked-team 安全边界和 helper surface。
- [x] 1.3 记录 routing policy 与 team entrypoints 的 spec delta。

## 2. Installer / Generator

- [x] 2.1 扩展 installer 与 shared runtime，加入 automatic durable-team routing 阈值和 tracked-team 元数据 helper。
- [x] 2.2 生成 `omx-team-auto.ps1`，作为可复用的 durable-team plan/apply helper。
- [x] 2.3 更新生成的 routing policy、leader profile、playbook 与 install manifest，暴露新的 helper 与路由语义。

## 3. Validation

- [x] 3.1 扩展 PowerShell 测试，使用更完整的 fake `omx` 验证 launch、reuse、switch、shutdown。
- [x] 3.2 验证“无 tracked team”“tracked team 匹配”“已有 unmanaged team”三类安全边界。
- [x] 3.3 运行 `openspec validate --all` 与 `python .\tools\run_openspec_guard.py --root .`。
