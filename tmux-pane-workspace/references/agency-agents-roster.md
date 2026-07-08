# Agency Agents — 可选专家角色来源

来源：https://github.com/msitarzewski/agency-agents（MIT 协议）

## 简介

Agency Agents 提供跨多个分组的 AI 专家角色，每个角色通常包含个性、工作流和交付物提示。它可以作为圆桌会议的**角色目录参考**：规划会议时，先按主题搜索相关专家，再把合适的人设改写成当前 workspace 中某个 pane 的角色定义。

这不是 `tmux-pane-workspace` 的硬依赖；没有安装 Agency Agents 时，也可以直接手写角色定义。

## 获取方式

当用户明确需要从 Agency Agents 下载职业技能时，可以临时克隆或下载上游仓库：

```bash
git clone https://github.com/msitarzewski/agency-agents /tmp/agency-agents
```

使用原则：

- 默认不把上游仓库作为本仓库 submodule，也不整包复制进 `c456-com/skills`。
- 只读取与当前任务相关的职业角色，提炼其人格、职责、工作流和交付物。
- 需要长期复用时，把提炼后的中文角色定义写入当前项目的团队配置或会议模板，而不是直接粘贴上游完整内容。
- 保留来源与 MIT 协议信息。

## 分组速查

| 分组 | 圆桌会议适用场景 |
|------|------------------|
| product | PM、趋势研究、迭代优先级 |
| engineering | 架构、开发、多 Agent、安全、SRE |
| design | UX、UI、品牌、创意 |
| marketing | 增长、SEO、社交媒体、中国平台 |
| paid-media | PPC、广告创意、追踪 |
| sales | 外拓、交易策略、销售管道 |
| security | 应用安全、云安全、威胁情报 |
| specialized | 商业策略、MCP、文化、合规 |
| testing | QA、可访问性、现实检验 |
| support | 分析、合规、财务追踪 |
| finance | FP&A、投资、税务 |
| academic | 人类学、心理学、历史 |

## 使用方式

规划圆桌会议时，按主题关键词搜索角色，例如：

- `platform`
- `knowledge`
- `growth`
- `monetization`
- `multi-agent`
- `security`

找到合适角色后，把其人格、职责和输出格式提炼到 `templates/roundtable-role-definition.md` 中，而不是直接把上游完整文件塞给每个 pane。

如果你有本地转换后的 `agents.json`，也可以用脚本筛选：

```python
import json
from pathlib import Path

data = json.loads(Path("agents.json").read_text())
matches = [
    agent for agent in data
    if "growth" in (agent.get("name", "") + agent.get("summary", "")).lower()
]
```
