# AGENTS.md — 给 AI 智能体的速查

本仓库：**vrbtc/credit-card-planner**（现金流日历 · 刷卡规划）

## 一句话

静态 GitHub Pages + 可选脚本；**邮件优先，人工补充填空**；滴答清单脚本已备好，**默认 dry-run，须用户授权才 `--apply`**。

## 路径

- 仓库根：`K:\Trae CN\credit-card-planner`（本机）
- 在线：https://vrbtc.github.io/credit-card-planner/
- 邮件工程：`K:\Trae CN\R BANK`（勿改其仪表盘主页面来塞本功能）

## 改什么文件

| 目标 | 文件 |
|------|------|
| 补充额度/账单日/贷款 | `data.js` |
| 邮件金额/还款日 | 跑 `scripts/refresh_bills_from_email.py` → `bills.json` |
| UI/免息/日历 | `index.html` |
| 滴答同步 | `scripts/ticktick_sync_planner.py`（先 dry-run） |
| 文档 | `README.md`（必更）、本文件 |

## 上线

```text
git add -A && git commit -m "..." && git push origin master
```

Pages 根目录即站点，无 build。

## 滴答清单（禁止擅自写入）

```text
# 安全预览
python scripts/ticktick_sync_planner.py

# 仅当用户明确授权：
set ALLOW_TICKTICK_SYNC=1
set TICKTICK_API_KEY=...
python scripts/ticktick_sync_planner.py --apply
```

清单名默认：`固定债务与还款日`。与账单项目的「信用卡还款」分离。

## 合并规则

1. 邮件有 → 用邮件  
2. 邮件无 → 用 `data.js` 补充  
3. YY = `source_label: "YY"`

完整说明见 [README.md](./README.md)。
