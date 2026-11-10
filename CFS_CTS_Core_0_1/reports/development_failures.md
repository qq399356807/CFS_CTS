# 开发阶段失败证据

第一次运行 `python3 run_tests.py` 时测试包装器有字面换行错误，运行在导入阶段停止；第二次修正包装器后，实际并发测试 `SEC-01` 失败，原因是账本的读尾/序号分配发生在跨进程锁之外。测试运行器捕获的原始断言摘要为：`AssertionError`，位置 `tests/test_security_extra.py:test_concurrency`（对 12 个子进程的序号/唯一 ID/哈希链完整性断言失败）。

已增加 `.lock` sidecar 对读、派生和写的全事务串行化；随后重新运行完整套件，结果 `PASS=16, FAIL=0, BLOCKED=1, INCONCLUSIVE=0`。上述失败为开发期真实缺陷，当前报告同时记录修复后结果；开发失败证据保留在本文件。平台文件锁及非协作访问风险仍未消除。
