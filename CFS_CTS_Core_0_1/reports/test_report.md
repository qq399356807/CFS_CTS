# CFS CTS Core 0.1 — 实测报告

运行环境：Python 3.13.5 / Linux-6.18.57-x86_64-with-glibc2.41

汇总：{'PASS': 18, 'FAIL': 0, 'BLOCKED': 1, 'INCONCLUSIVE': 0}

> 本报告为本地 Python 3.13/Linux 运行结果。CORE-06 的 PASS 仅表示“本地同时重建可成功”的安全边界演示，不代表抵御攻击。无外部锚点。

| ID | 测试 | 状态 | 结果 |
|---|---|---|---|
| CORE-01 | UTC rollback | **PASS** | UTC 回拨与逻辑计数器检测通过 |
| CORE-02 | UTC jump | **PASS** | UTC 跳变检测通过 |
| CORE-03 | event deletion | **PASS** | 序号缺口与哈希链断裂检测通过 |
| CORE-04 | content tamper | **PASS** | 事件内容哈希篡改检测通过 |
| CORE-05 | event reorder | **PASS** | 事件重排检测通过 |
| CORE-06 | local ledger+anchor rebuild | **PASS** | 确认边界：同权限攻击者可同时重建本地账本与锚点；无外部锚点 |
| CORE-07 | simulated reboot | **PASS** | 新会话 boot ID 与逻辑计数器重置检测通过 |
| SEC-01 | concurrent writes | **PASS** | 12 个并发进程全部成功，12 条事件唯一且哈希链有效 |
| SEC-02 | duplicate event ID | **PASS** | 重复事件 ID 被拒绝 |
| SEC-03 | partial write/crash tail | **PASS** | 截断 JSONL 尾部被检测 |
| SEC-04 | JSONL truncation | **PASS** | JSONL 截断被检测 |
| SEC-05 | anchor rollback boundary | **PASS** | 连续检查点有效；本地文件整体重写仍不受保护 |
| SEC-06 | missing parent | **PASS** | 缺失因果父事件被拒绝 |
| SEC-07 | oversized event | **PASS** | 超大事件被拒绝 |
| SEC-08 | Unicode/canonicalization | **PASS** | UTF-8 往返与独立规范化校验通过 |
| SEC-09 | duplicate batch submit | **BLOCKED** | 0.1 尚未实现批量提交 API |
| SEC-10 | invalid clock input | **PASS** | 非有限时钟输入被拒绝 |
| SEC-11 | lock failure is fail-closed | **PASS** | 注入锁获取失败后追加被中止，账本未改变 |
| SEC-12 | intermediate anchor checkpoint tamper | **PASS** | 中间检查点摘要篡改被检测 |

## 风险/未实现

- CORE-06 使用本地模拟锚点；同权限攻击者同时重建账本与锚点仍无法被检测。
- 尚未配置独立管理的远程锚点。
- 跨平台 CI 已配置；文件锁与 fsync 的保证仍限于实际通过验证的平台和文件系统。
- 尚未实现批量提交幂等性。
