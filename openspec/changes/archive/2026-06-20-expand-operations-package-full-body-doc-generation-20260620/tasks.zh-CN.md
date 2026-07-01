# 任务：把运营包扩展为正文级文档生成

## Stage A：冻结方案与契约

- [x] 创建本 OpenSpec change，包含 proposal、design、management、tasks 和 delta specs。
- [x] 创建双语正文级实施方案。
- [x] 在 `docs_bilingual/docs_registry.yaml` 中登记正文级实施方案。
- [x] 验证 Stage A。
- [x] 提交 Stage A 并合入本地 `main`。

## Stage B：实现 live runtime 和正文层

- [x] 扩展 `tools/generate_operations_package.py`，在 `docs_bilingual/operations_packages/` 下生成 48/60 正文层。
- [x] 扩展 `tools/check_operations_package_docs.py`，校验正文数量、双语配对、registry 覆盖、I/T/O 顺序与非空内容、裁剪模式、编码和串包隔离。
- [x] 扩展 `test/operations_package_docs.test.py`，覆盖正文全集数量、配对、I/T/O、裁剪、registry、写入幂等和串包负例。
- [x] 生成 Codex 持久化团队正文文档：48 个英文主文件和 48 个 zh-CN 伴随文件。
- [x] 生成一人公司正文文档：60 个英文主文件和 60 个 zh-CN 伴随文件。
- [x] 在 `docs_bilingual/docs_registry.yaml` 中登记每一对生成的正文文档。
- [x] 运行聚焦运营包检查和测试。
- [x] 运行 OpenSpec、repository guard、本地 CI 和本地 MR review gate。
- [x] 提交 Stage B 并合入本地 `main`。
- [x] 在 Stage B 通过验证且 stable specs 同步后归档该 OpenSpec change。

## 远端发布

- [x] 除非用户显式授权 GitLab/GitHub 发布，否则停在远端发布门。
