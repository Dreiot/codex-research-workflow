<p align="right"><a href="./README.md">English</a> · <strong>简体中文</strong></p>

<p align="center"><img src="./assets/readme/hero.svg" width="100%" alt="Codex Research Workflow"></p>

# Codex Research Workflow

本仓库包含两个按需加载、互相配合的 Codex Skill：

- `$codex-research-workflow` 负责科研执行、Git 身份、长期方向、当前阶段、实验产物、证据、审查和交接。
- `$research-artifact-cleanup` 只负责历史科研产物清理；必须先生成与项目状态绑定的计划，再按用户批准的精确范围执行。

默认科研循环仍是：最小实现 → 真实数据运行 → 指标 → 问题定位 → 方向调整 → 论文证据。普通 smoke、探索运行和调试不会自动变成正式审查 Gate。

## 三份权威文件

| 文件 | 职责 |
|---|---|
| `AGENTS.md` | 稳定规则与实验根目录约定 |
| `docs/PROJECT_CORE.md` | 精简的长期方向；每个往期方向只保留一条综合记录 |
| `docs/CURRENT_STAGE.md` | 只记录当前 Gate、accepted identity、findings 和下一动作 |

内部标识 `codex-project-core` 与 `codex-handoff-state` 保持兼容。聊天摘要不能代替仓库权威状态。

## Workflow 命令

```text
workflow.py init                 # 默认只生成计划；--apply 必须带相同 plan ID
workflow.py migrate              # 迁移旧治理项目，不移动旧实验产物
workflow.py audit
workflow.py prepare-experiment   # 需要持久运行产物时才创建
workflow.py prepare-evidence     # 需要 Work 判断或证据提升时才创建
workflow.py validate-evidence
workflow.py record-review
workflow.py resume-prompt
```

`initialize` 仅作为旧自动化的未公开兼容别名保留。

新项目 `init` 会检查精确目录、嵌套 Git、待上传文件、敏感/超大文件、远端历史，以及 GitHub owner/name/visibility。只使用 `main`，不会扩展分支，也不会覆盖或强推已有历史。

旧项目 `migrate` 同样采用 plan/apply，只补充缺失权威文件、实验策略和 ignore 规则；不会迁移实验产物、压缩文档或改变科研内容。

## 实验产物

默认根目录为 `experiments/`，也可在 `AGENTS.md` 中指定其他仓库相对路径。所有目录按需创建。

```text
experiments/
├── scripts/       跟踪的实验入口
├── configs/       跟踪的配置
├── registry/      跟踪的精简登记与重要清理记录
├── evidence/      跟踪的 Work 决策证据包
├── runs/          忽略的运行输出
├── .tmp/          忽略的临时文件和清理计划
└── quarantine/    忽略的待裁定产物
```

核心方法代码继续放在 `src/` 或项目已有代码区。原始数据集和外部数据不进入实验根目录。

探索结果若只用于下一次可逆探索，Codex 回复中的输出即可。若 Work 要据此改变方向、方法、基线、数据划分、指标、claim，或采纳为正式证据，则生成 `experiments/evidence/<experiment-id>/<candidate-id>/`：至少包含 `manifest.json` 与 `analysis_report.md`；仅在确有数值指标时增加 `metrics.json`。

## 清理事务

清理只允许六种分类：`keep_formal_evidence`、`keep_negative_evidence`、`keep_active`、`delete_reproducible`、`delete_technical_failure`、`unknown`。`unknown` 永不删除。

只有已提交的 `PROJECT_CORE.md` 修改确实终止、拒绝、替代主要方向，或使旧运行因核心组件变化而失效时，Workflow 才自动联动 Cleanup 生成只读计划，并在用户审批前停止。措辞、引用、证据等级或 claim 收窄不会自动触发清理。

详细 JSON 计划位于被 Git 忽略的临时目录。重要清理核验通过后生成 `experiments/registry/cleanup/<cleanup-id>.json`。当前运行中预先标记为临时、且成功后已无引用的文件可由 Workflow 直接删除，不进入历史清理事务。

## Browser Work 契约

每个可执行 Work Goal 必须显式调用 `$codex-research-workflow`；清理 Goal 同时调用两个 Skill。[Work Response Contract](./skills/codex-research-workflow/references/work-response-contract.md) 保留原有四段式输出与正式审查边界，它是输出协议，不是强制状态机。

## 安装

```bash
npx skills add Dreiot/codex-research-workflow
```

安装两个路径：

```text
skills/codex-research-workflow
skills/research-artifact-cleanup
```

Windows 示例：

```powershell
py -3 "$env:USERPROFILE\.codex\skills\codex-research-workflow\scripts\workflow.py" audit --repo C:\项目路径
```

可选生命周期 Hook 采用 fail-open，只注入精简权威/Gate 指针；显式 `audit` 仍然 fail-closed。正式 reviewer Hook 保留。

## 验证

```bash
python -m py_compile skills/codex-research-workflow/scripts/workflow.py skills/codex-research-workflow/scripts/hook.py skills/research-artifact-cleanup/scripts/cleanup.py
python -m unittest discover -s tests -v
```

许可证：Apache-2.0。
