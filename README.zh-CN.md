<p align="right">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Codex Research Workflow 将连续科研执行与稳定规则、长期战略和可恢复项目状态结合。">
</p>

<p align="center">
  <img src="./assets/readme/workflow-tags.svg" width="100%" alt="探索优先、权威状态、claim 感知，以及 Codex 与 Browser Work 协作。">
</p>

长期科研任务容易在多轮对话、自动压缩和跨任务切换后发生状态漂移。**Codex
Research Workflow** 将探索优先的科研执行循环与三份仓库权威文件结合，使用确定性脚本
核验 schema 与 Git，并在任务恢复或自动压缩后重新注入正确的战略和阶段上下文。

它适用于科研软件、论文实验流水线、证据 Gate，以及任何不能只依赖“看起来合理的聊天总结”
的项目。

## 三层权威协议

| 权威文件 | 时间尺度 | 负责内容 | 禁止承担 |
| --- | --- | --- | --- |
| `AGENTS.md` | 稳定 | 操作规则、权限、验证、Git、审查和 claim 边界 | 当前 Gate 或临时进度 |
| `docs/PROJECT_CORE.md` | 长期 | 研究问题、目标贡献、创新假设、组件图谱、已探索方向、证据等级和 claim 上限 | branch、HEAD、当前 verdict 或下一动作 |
| `docs/CURRENT_STAGE.md` | 动态 | 分支、当前 Gate、被审查 candidate、verdict、未解决问题和唯一下一动作 | 长篇战略或项目历史 |

这种拆分可以防止旧交接总结悄然变成第二个真相来源。

<p align="center">
  <img src="./assets/readme/workflow.svg" width="100%" alt="默认连续实证迭代，仅在正式提升为科研基线或论文证据时进行独立审查。">
</p>

## Skill 能做什么

| 命令 | 结果 | 是否写文件 |
| --- | --- | --- |
| `audit` | 校验两个 JSON 状态块、必需章节、报告路径、Git 祖先关系、项目标识和旧交接文件 | 否 |
| `initialize` | 只创建缺失文件，并使用明确标记为 unaudited 的保守占位内容 | 是 |
| `record-review` | 将精确 candidate SHA、固定 verdict、findings、报告路径和下一 Gate 写入 `CURRENT_STAGE.md` | 是 |
| `resume-prompt` | 生成 Codex 或浏览器审查对话的短恢复 Prompt | 否 |

生命周期 Hook 会在启动、恢复、清空和自动压缩时注入精简的战略/Gate 摘要；可选的
reviewer Hook 只约束显式启动的 `research-reviewer`。普通 shell 命令和任务结束不再
自动运行 handoff audit。**Hook 永远不会修改仓库。**

## Browser Work 输出契约

生成的 Work 恢复 Prompt 会链接公开的
[输出契约](./skills/maintain-codex-handoff/references/work-response-contract.md)。
Work 的回复采用审查结果、设计目标、验收目标，以及至多一个包含单一 Codex Goal 的
Markdown 指令块。该契约只是输出格式，不是强制审查状态机。探索性实现和真实数据工作
不需要 review-state；机械验收通过后可在同一回复直接签发下一 Goal。只有用户明确授权时，
代理才能修改该公共契约。

## 安装

```bash
npx skills add Dreiot/codex-research-handoff
```

也可以直接让 Codex 安装：

```text
请从 https://github.com/Dreiot/codex-research-handoff 安装 Skill，
路径为 skills/maintain-codex-handoff。
```

安装后的调用名保持为：

```text
$maintain-codex-handoff
```

## 第一次使用

Windows PowerShell：

```powershell
py -3 "$env:USERPROFILE\.codex\skills\maintain-codex-handoff\scripts\handoff.py" initialize --repo C:\项目路径
py -3 "$env:USERPROFILE\.codex\skills\maintain-codex-handoff\scripts\handoff.py" audit --repo C:\项目路径
```

macOS 或 Linux：

```bash
python3 ~/.codex/skills/maintain-codex-handoff/scripts/handoff.py initialize --repo /项目路径
python3 ~/.codex/skills/maintain-codex-handoff/scripts/handoff.py audit --repo /项目路径
```

`initialize` 不会推断科研结论。它只创建 `unaudited` 的 `PROJECT_CORE.md`，之后必须由
项目负责人或合格审查者根据仓库证据完成战略审计。

## 配置 Hook 与独立审查者

将 [hooks.template.json](./examples/hooks.template.json) 中需要的条目合并到
`~/.codex/hooks.json`，不要覆盖已有 Hook。Windows 模板使用 `%USERPROFILE%`；如果
当前 Hook runner 不展开环境变量，请改成绝对路径。

[research-reviewer.toml](./examples/research-reviewer.toml) 是可选的只读审查者，安装到
`~/.codex/agents/research-reviewer.toml`。当浏览器 ChatGPT 已经完成合格的独立审查时，
不应再重复启动它。

## 执行与审查规则

默认采用连续实证流程：

```text
最小实现 → 真实数据运行 → 性能指标 → 问题定位 → 方向调整 → 论文证据
```

普通实现、测试、调试、数据处理、本地 smoke、探索实验、调参和指标生成不需要独立审查
或 review-state。只有明确准备接受主要实现基线、冻结正式论文实验、采纳关键结果、改变
核心方法或提升论文 claim 时，才进行一次合格的独立审查：

- 浏览器审查必须独立于实现，明确 exact base/candidate SHA，检查真实 diff 与证据，
  并返回 P0/P1/P2 与固定 verdict。
- 只有在缺少合格浏览器审查、证据不完整或冲突、或用户要求第二意见时，才使用
  `research-reviewer`。
- 正式提升被拒绝或阻塞时，先记录结论再修正，以保留决策和 candidate 身份。
- 机械验收不产生第二次审查；通过后 Work 可以立即签发下一 Goal。

Git 历史保持实现与审查状态分离：

```text
candidate implementation commit
review-state governance-docs commit
```

新的 `record-review` 输入应声明 `candidate_kind`。接受的 `implementation` candidate 成为新的
`accepted_code_commit`；接受的 `docs_only` candidate 保留此前 accepted code。
`REJECT`、`BLOCKED` 和 review-state commit 都不会替换 accepted code。

探索性 smoke 只是诊断证据，不能自动升级为论文证据；正式运行冻结数据边界、配置、
指标、统计单位、comparators、停止条件和 provenance。范围已经冻结并获得授权后，
Skill 不再增加重复的逐次执行许可。

## 自动压缩不等于交接

自动压缩是同一个 Codex 任务内的正常连续性，不需要停手、强行 checkpoint commit 或
新建任务。应在证据改变权威状态时落库；只有主动新建 Codex/浏览器对话、压缩后确实
丢失关键约束，或到达自然 Gate 边界时，才执行显式交接。

## 安全边界

- Skill 不决定科研结论。
- Hook 只警告和注入上下文，不是权限沙箱。
- 脚本不会自动 commit 或 push。
- 浏览器 ChatGPT 不会自动加载本机 Hook、Skill 或 memory。
- 私有数据、大日志、生成产物和密钥不得进入权威交接文件。
- `CODEX_HANDOFF.md` 和 `LATEST_STATE.md` 被视为旧动态状态文件，避免形成多个真相来源。

## 验证

```bash
python -m unittest discover -s tests -v
python -m py_compile skills/maintain-codex-handoff/scripts/handoff.py skills/maintain-codex-handoff/scripts/hook.py
```

测试使用临时 Git 仓库验证初始化幂等性、schema 审计、恢复 Prompt、迁移兼容性和 Hook
只读行为。

## 许可证

[MIT](./LICENSE)
