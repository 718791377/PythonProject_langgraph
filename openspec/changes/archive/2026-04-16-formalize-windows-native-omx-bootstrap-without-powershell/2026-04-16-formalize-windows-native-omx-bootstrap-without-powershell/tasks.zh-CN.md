## 1. 合同

- [x] 1.1 定义不依赖 powershell.exe 的正式 Windows native_omx bootstrap 合同
- [x] 1.2 定义针对全局安装的 repo-managed repair 或 verification 路径

## 2. 实施

- [x] 2.1 增加可重复执行的 repo-managed repair 或 verification script
- [x] 2.2 验证修复后 native_omx prompt-worker launch 能成功

## 3. 验证

- [x] 3.1 验证 backup 与 rollback 预期仍然明确
- [x] 3.2 运行 `openspec validate --all` 并确认该 change 已达到 apply-ready
