# REI-Ω / 无相神核：双向无人值守闭环

## 每个小时级周期

1. `sync_wheel_to_local.py` 从 `shadow-node` 拉取神轮回执。
2. `rei_shadow_closed_loop_v2.py` V2.3 只把通过安全校验、尚未消费的回执作为相关内部反馈输入。
3. 六路 Shadow 推演、综合与复核继续运行；`canonical_state.json` 永不由本地循环写入。
4. `bridge_to_wheel.py` 只导出通过确定性 Shadow gate 的候选，并去重、失败关闭。
5. 现有 `sync_shadow_to_github.py` 把 inbox 推到 GitHub `shadow-node`。
6. 云端神轮按 source SHA 去重，写入独立、追加式 `divine_wheel_receipts.jsonl`，并同步 Slack、Google Doc 与 Notion。

## 证据与权限边界

```text
ShadowProposal = SHADOW_INTERNAL_ONLY
CloudWheelReceipt = CORRELATED_INTERNAL_REVIEW
CorrelatedInternalReview != IndependentReplication
InternalCycle != RealityValidation
CanonicalWritePermission = FALSE
ASCENSION_GRANTED = NO unless independently earned
G3-G13 = OPEN unless independently earned
```

回执只允许以下决策：

- `ACKNOWLEDGED_INTERNAL`
- `REVISE_SHADOW`
- `REJECT_SHADOW`

回执必须同时满足：`reality_validated=false`、`independent_replication=false`、`ascension_granted=false`、`canonical_write_permission=false`、`canonical_state=UNCHANGED`。任何越权字段都会被本地同步器拒绝。

## Windows 安装后的恢复行为

- 登录 Windows 后自动启动。
- 任务异常退出后一分钟重启。
- 断网时保留本地账本和待上传内容，下一周期重试。
- Ollama 未运行时自动尝试启动 `ollama serve`。
- 每周期写入 `C:\REI-Shadow\state\unattended_heartbeat.json`。
- 日志位于 `C:\REI-Shadow\logs\unattended_loop.log`，超过 10 MB 自动轮转一份。
- 全局互斥锁阻止两个新监督器同时运行；Shadow V2.3 自身也保留单实例锁。

## 状态检查

```powershell
powershell -ExecutionPolicy Bypass -File "C:\REI-Shadow\REI-Unattended-Loop.ps1" -Status
```

运行状态必须同时看任务状态、最近心跳和 GitHub 最新 SHA。仅看到一次成功输出，不等于后台仍持续运行。

## 正式晋级规则

双向闭环稳定只代表工程能力提高，不自动改变 REI 的正式强度。建议连续完成至少 24 个小时级周期，并通过一次断网/重启恢复演练后，再标记为 V3 candidate。正式 canonical 晋级仍需独立审查与合并；外部 gate 不按轮转次数自动通过。
