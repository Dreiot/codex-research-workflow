<p align="right"><a href="./README.md">English</a> · <strong>简体中文</strong></p>

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Codex Research Workflow 将项目权威状态连接到快速实验、可审查证据与经审批的清理">
</p>

# Codex Research Workflow

两个按需加载、互相配合的 Codex Skill，面向既要快速推进、又不能丢失精确科研状态的长期研究仓库。

- **`$codex-research-workflow`** 统一 Git 身份、长期方向、当前 Gate、实验产物、证据、审查与交接。
- **`$research-artifact-cleanup`** 只通过用户批准、与项目状态绑定的精确计划清理过时科研产物。

探索保持轻量；会改变方法、基线、数据划分、指标、停止条件或论文 claim 的决定，必须落成 Git 可访问证据。

<p align="center">
  <img src="./assets/readme/system-map.svg" width="100%" alt="Git 权威进入最小科研执行、证据候选与明确方向决策">
</p>

## 为什么需要它

长期科研容易在聊天摘要、旧报告、历史运行与真实 worktree 之间发生漂移。本 Workflow 给 Codex 和 Browser Work 一组很小的权威入口，每次工作前可以重新恢复状态，同时不会把普通实现、smoke 或探索运行变成审查负担。

默认流程始终是：

```text
最小实现 → 真实数据运行 → 指标 → 问题定位 → 方向调整 → 论文证据
```

## 两个 Skill，一份契约

| Skill | 负责 | 不负责 |
|---|---|---|
| [`$codex-research-workflow`](./skills/codex-research-workflow/SKILL.md) | 初始化、迁移、权威审计、实验清单、证据候选、审查状态和恢复 Prompt | 把每次探索提升为正式 Gate |
| [`$research-artifact-cleanup`](./skills/research-artifact-cleanup/SKILL.md) | 元数据盘点、六类清理分类、不可变计划身份、迁移/删除/核验 | 自行推断科研价值，或从未审批清单直接删除 |

每个可执行 Browser Work Goal 都调用 Workflow；历史或批量清理同时调用两个 Skill。公开的 [Work Response Contract](./skills/codex-research-workflow/references/work-response-contract.md) 规定四段式 Work 回复和正式审查边界。

## 第一次成功运行

安装仓库中的两个 Skill：

```bash
npx skills add Dreiot/codex-research-workflow
```

审计一个已有治理项目：

```powershell
py -3 "$env:USERPROFILE\.codex\skills\codex-research-workflow\scripts\workflow.py" audit --repo C:\项目路径
```

Codex 打开的项目根与精确 Git 根必须是同一目录。嵌套或双根结构会停止，等待显式根目录迁移。

旧治理项目先只查看迁移计划：

```powershell
py -3 "$env:USERPROFILE\.codex\skills\codex-research-workflow\scripts\workflow.py" migrate --repo C:\项目路径
```

`init` 和 `migrate` 默认只生成计划。`--apply` 必须提供完全相同的 `plan_id`；Git 或文件状态变化会使审批失效。

## 权威文件模型

| 权威文件 | 时间尺度 | 记录 | 不记录 |
|---|---|---|---|
| `AGENTS.md` | 稳定 | 仓库规则、权限、审查/Git 边界、实验根目录 | 当前进度 |
| `docs/PROJECT_CORE.md` | 长期 | 研究问题、主方向、创新假设、组件、往期方向综合裁定、claim 上限 | 当前分支、Gate 或下一动作 |
| `docs/CURRENT_STAGE.md` | 当前 | 分支、当前 Gate、reviewed/accepted identity、findings、唯一下一动作 | 编年历史 |

Git 与已提交证据保持权威。聊天摘要只是入口，不是状态。改名前创建的项目继续兼容 `codex-project-core` 与 `codex-handoff-state` 内部标识。

## 实验产物不再污染仓库根目录

默认实验根目录为 `experiments/`；也可在 `AGENTS.md` 中声明其他项目相对路径。没有真实产物需求时不会预建任何目录。清理盘点仍从完整项目根开始，包括 ignored 本地产物。

```text
experiments/
├── scripts/       跟踪的实验入口
├── configs/       跟踪的配置
├── registry/      跟踪的精简决策与重要清理记录
├── evidence/      跟踪的 Work 证据候选
├── runs/          忽略的生成运行结果
├── .tmp/          忽略的临时文件与清理计划
└── quarantine/    忽略的待裁定产物
```

核心方法代码继续放在项目已有源码区域；原始数据集和外部数据不进入实验根目录。

<p align="center">
  <img src="./assets/readme/evidence-candidate.svg" width="100%" alt="探索输出保持轻量，而会改变方向的 Work 决策需要跟踪证据候选">
</p>

若 Browser Work 要采纳某个结果，或据此改变方向、方法、基线、数据划分、指标或 claim，则先建立 `experiments/evidence/<experiment-id>/<candidate-id>/`。其中包括 `manifest.json`、`analysis_report.md`；只有确实存在数值指标时才增加 `metrics.json`。结构校验只能证明可访问性与完整性，不能代替科研充分性判断。

## 清理必须停下来审批

<p align="center">
  <img src="./assets/readme/cleanup-gate.svg" width="100%" alt="清理盘点生成状态绑定计划，并在迁移或删除前暂停等待用户审批">
</p>

清理严格使用六类分类：

| 默认保留 | 仅有证据且审批后可删除 |
|---|---|
| `keep_formal_evidence` · `keep_negative_evidence` · `keep_active` · `unknown` | `delete_reproducible` · `delete_technical_failure` |

只有已提交的 `PROJECT_CORE.md` 调整确实终止、拒绝、替代主要方向，或使它因核心组件变化而过时时，才触发只读清理计划。措辞、引用、证据等级或 claim 收窄不会触发清理。详细计划保持 Git 忽略；重要清理核验通过后生成 `experiments/registry/cleanup/<cleanup-id>.json`。

## 只在风险上升时审查

| 工作通道 | 审查行为 |
|---|---|
| 探索 | 实现、smoke、调试、调参、指标和诊断无需 review-state |
| 自然实现候选 | 新代码成为稳定依赖前，Browser Work 审查已推送的精确 diff；默认不形成正式状态事务 |
| 正式提升 | 接受主要基线、冻结论文评估、采纳关键结果、改变核心方法或提升 claim 时进行一次合格审查 |

正式 verdict 为 `ACCEPT`、`ACCEPT_WITH_P2`、`REJECT` 或 `BLOCKED`。P0/P1 必须 `REJECT`；P2 不阻塞。机械核验不是第二次审查。

## 命令接口

| 命令 | 用途 |
|---|---|
| `workflow.py init` | 完成 Git/GitHub 安全检查后计划并初始化新的 `main` 仓库 |
| `workflow.py migrate` | 补充新策略，不移动产物、不重写科研内容 |
| `workflow.py audit` | 遇到实质权威或 Git 冲突时 fail closed |
| `workflow.py prepare-experiment` | 按需生成忽略的 `research-experiment-run/v1` 清单 |
| `workflow.py prepare-evidence` | 建立跟踪的 `research-evidence-candidate/v1` 证据包 |
| `workflow.py validate-evidence` | 校验 schema、报告章节、hash 和 Git 可访问性 |
| `workflow.py record-review` | 记录一次明确的正式提升审查 |
| `workflow.py resume-prompt` | 生成精简的 Codex 或 Browser Work 恢复 Prompt |
| `cleanup.py plan` | 盘点指定路径并生成被忽略的状态绑定计划 |
| `cleanup.py apply` | 对已批准 plan ID 执行 `relocate`、`delete` 或 `verify` |

`initialize` 仅保留为旧版“只创建缺失文件”自动化的未公开兼容别名。

## Hook、边界与兼容性

- 可选 `SessionStart` Hook 只读且 fail-open，仅注入精简权威/Gate 指针；显式 `audit` 仍然 fail-closed。
- reviewer Hook 保留正式审查边界，不会因为咨询过 reviewer 就自动生成状态事务。
- 新项目初始化拒绝嵌套仓库、可疑上传范围、敏感/超大文件和已有远端历史，永不 force-push。
- Cleanup 盘点只读取元数据、跟踪引用和 Git 状态，不读取大型运行内容或原始数据来擅自分类。
- 兼容 Contract 路径与新路径保持字节一致，旧 ChatGPT Work Project Instruction 在改名后仍能继续读取。

## 当前验证

仓库通过 **11 项集成测试**覆盖：初始化与 `main` 推送、迁移、按需运行清单、证据校验、审查状态语义、Hook 行为、清理计划身份、审批后删除及清理核验；CI 面向 Windows 与 Linux。

```bash
python -m py_compile skills/codex-research-workflow/scripts/workflow.py skills/codex-research-workflow/scripts/hook.py skills/research-artifact-cleanup/scripts/cleanup.py
python -m unittest discover -s tests -v
```

贡献检查见 [CONTRIBUTING.md](./CONTRIBUTING.md)。采用 [Apache-2.0](./LICENSE) 许可证。
