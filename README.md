# 刷卡规划助手 · Credit Card Planner

独立静态页，与 [bank-bill-extractor](https://github.com/vrbtc/bank-bill-extractor) **完全分离**，不改动原账单仪表盘。

## 功能

1. **今天刷哪张最划算** — 按「今天消费」计算各卡免息天数，推荐最长的
2. **每张卡免息期** — 今日免息天数、所属账单日、对应还款日、理论最长免息
3. **每月固定债务还款日** — 长期贷款 / 固定月供日历与合计
4. **滴答清单同步（可选）** — 脚本已就绪，**默认 dry-run，需你明确授权才写入**

## 在线地址

部署完成后：

- https://vrbtc.github.io/credit-card-planner/

## 本地预览

用任意静态服务器打开根目录，或直接双击 `index.html`（部分浏览器对 `file://` 限制较少，本页无模块依赖，可直接打开）。

```bash
# 可选
npx --yes serve .
```

## 修改数据

编辑根目录 **`data.js`**：

```js
cards: [
  { name: "浦发银行", statement_day: 5, due_day: 24, note: "", enabled: true },
  // ...
],
loans: [
  { name: "房贷", amount: 8500, due_day: 10, note: "", enabled: true },
]
```

| 字段 | 含义 |
|------|------|
| `statement_day` | 账单日（每月几号） |
| `due_day` | 还款日（每月几号） |
| `amount` | 贷款每月金额（仅 loans） |
| `enabled` | `false` 则不参与计算/展示 |

改完后提交并 push，GitHub Pages 会自动更新（或手动在仓库 Settings → Pages 确认）。

> 当前 `statement_day` 有一部分是按账单**邮件发送日**估算的，请用银行 APP 里的真实账单日覆盖。

## 滴答清单集成（需授权）

脚本：`scripts/ticktick_sync_planner.py`

```powershell
# 1) 仅预览，不创建任务
python scripts/ticktick_sync_planner.py

# 2) 你确认无误后，授权写入
$env:ALLOW_TICKTICK_SYNC = "1"
$env:TICKTICK_API_KEY = "你的滴答 OpenAPI Key"
python scripts/ticktick_sync_planner.py --apply
```

- 清单名默认：`固定债务与还款日`（可用 `--project` 改）
- 与账单提取系统的「信用卡还款」清单**分开**，避免互相覆盖
- 未设置 `ALLOW_TICKTICK_SYNC=1` 时即使加了 `--apply` 也会拒绝写入

## 与原项目关系

| | 账单仪表盘 | 本仓库 |
|--|-----------|--------|
| 仓库 | `bank-bill-extractor` | `credit-card-planner` |
| 数据源 | 邮箱账单 | 你配置的账单日/还款日/贷款 |
| 页面 | 待还金额、紧急度 | 免息期、刷哪张、固定债务日历 |
| 滴答清单 | 按账单金额同步 | 按固定还款日提醒（可选） |

## 安全提示

- **不要**把 GitHub Token、邮箱密码、滴答 Key 写进本仓库
- Token 若曾在聊天中明文发送，请到 GitHub 撤销并重新生成
