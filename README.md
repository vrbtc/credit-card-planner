# 现金流日历 · 刷卡规划

> **给人类与 AI 智能体的完整说明书**  
> 仓库：https://github.com/vrbtc/credit-card-planner  
> 在线页：https://vrbtc.github.io/credit-card-planner/  
> 与 [bank-bill-extractor](https://github.com/vrbtc/bank-bill-extractor) **完全分离**，不修改原账单仪表盘。

---

## 1. 项目是什么

独立 **GitHub Pages 静态站** + 可选 **Python 脚本**，用来：

1. **今天刷哪张卡最划算**（最长免息 / 空当接龙）
2. **日历管卡**：上方出账日、下方还款日；格子显示账单金额；点日期看详情
3. **信用卡**：还款日/金额/额度（邮件 + 人工补充）
4. **长期贷款 / 固定月供**：还款日历、本金快照与等额本息估算
5. **滴答清单同步（已写好，默认不写入）**：用户明确授权后，才把固定还款写进滴答清单

交互参考「卡神日历」。

---

## 2. 仓库结构

```
credit-card-planner/
├── index.html          # 单页 UI + 全部前端逻辑
├── data.js             # 人工配置：卡表补充额度/账单日、贷款、合并规则说明
├── bills.json          # 邮件提取快照（金额/还款日/部分额度/YY）
├── README.md           # 本文件（部署 / 使用 / 授权同步）
├── .gitignore
└── scripts/
    ├── refresh_bills_from_email.py   # 从 R BANK 邮箱重拉账单 → 写 bills.json
    └── ticktick_sync_planner.py      # 滴答清单：默认 dry-run，授权后 --apply
```

| 文件 | 作用 |
|------|------|
| `index.html` | 页面；合并邮件+补充；免息；日历；贷款估算 |
| `data.js` | **人工补充**卡额度/账单日/还款日兜底；**贷款**月供与本金快照 |
| `bills.json` | **邮件**提取结果缓存 |
| `scripts/refresh_bills_from_email.py` | 依赖本机 `K:\Trae CN\R BANK` 邮箱配置，刷新 `bills.json` |
| `scripts/ticktick_sync_planner.py` | 固定债务 + 信用卡还款日 → 滴答清单 |

---

## 3. 数据合并规则（核心，必须遵守）

```
邮件有值  →  以邮件为准（还款日、账单日、待还金额、邮件解析到的额度…）
邮件无值  →  用 data.js 人工补充（用户提供的总额度、现账单日等）
```

- 页面表格会标注来源：**「邮件」** 或 **「补充」**
- **YY 卡**：QQ 邮箱 `source_label=YY`（如长安银行）强制橙色 **YY** 徽章
- **不要**用静态配置覆盖邮件里已有的还款日/金额

### 3.1 data.js 卡表（补充）

字段示例：

```js
{
  name: "浦发银行",
  last4: "8182",
  statement_day: 4,      // 现账单日（邮件无时用）
  due_day: 24,           // 固定还款日（邮件无时用；邮件有 due_date 则被覆盖）
  credit_limit: 52500,   // 总额度（邮件无时用）
  short: "浦",
  color: "#003b8e",
  enabled: true
}
```

当前主卡补充额度合计 **¥651,200**（11 张，不含长安 YY）。

### 3.2 data.js 贷款

```js
{
  category: "房贷",
  bank: "建行",
  monthly: 3014,
  due_day: 15,
  principal_total: 670000,
  principal_left: 579406.84,
  principal_as_of: "2026-07-27",
  amortize: "epi",          // epi=等额本息 | installment=分期近似全本金
  rate_annual: 3.2,         // 3.2 或 0.032 均可
  enabled: true
}
```

- **月供**：固定，不自动变  
- **剩余本金**：快照 + 按期估算（非银行实时）；标「估算」

### 3.3 bills.json（邮件）

由 `scripts/refresh_bills_from_email.py` 生成，字段含：

`bank_name`, `source_label`, `amount`, `due_date`, `due_day`, `statement_date`, `statement_day`, `credit_limit`, …

---

## 4. 部署（GitHub Pages）

### 4.1 已部署地址

- Pages：https://vrbtc.github.io/credit-card-planner/  
- 源：`master` 分支根目录（`index.html` + `data.js` + `bills.json`）

### 4.2 更新上线步骤

```powershell
cd "K:\Trae CN\credit-card-planner"
# 改 data.js / index.html / bills.json 后：
git add -A
git commit -m "chore: update planner data"
git push origin master
```

约 1 分钟后刷新 Pages。无需 build 工具。

### 4.3 新建环境时

```powershell
# 已有仓库则 clone
git clone https://github.com/vrbtc/credit-card-planner.git
cd credit-card-planner

# 启用 Pages：Settings → Pages → Branch: master / (root)
# 或 gh：
gh api -X POST repos/vrbtc/credit-card-planner/pages -f build_type=legacy -f source[branch]=master -f source[path]=/
```

---

## 5. 本地预览

```powershell
cd "K:\Trae CN\credit-card-planner"
# 方式 A：直接双击 index.html（无打包依赖）
# 方式 B：
npx --yes serve .
```

页面会请求 `./bills.json`（同源），`file://` 下 fetch 可能失败，建议用本地静态服务器。

---

## 6. 刷新邮件账单

**前置**：本机存在 `K:\Trae CN\R BANK`，且 `config.json` 配置了邮箱（主邮 + YY 的 QQ 邮）。

```powershell
cd "K:\Trae CN\credit-card-planner"
python scripts/refresh_bills_from_email.py
git add bills.json
git commit -m "chore: refresh bills from email"
git push origin master
```

会：

1. 登录邮箱提取账单（金额、还款日、能解析的额度/账单日、YY）  
2. 写回 `bills.json`  
3. 同步写 `R BANK/this_month_bills.json`（不碰原仪表盘页面也可）

---

## 7. 滴答清单模块（已就绪，默认不写入）

### 7.1 状态

| 项 | 说明 |
|----|------|
| 脚本 | `scripts/ticktick_sync_planner.py` **已写好** |
| 默认 | **dry-run**，只打印任务列表 |
| 写入条件 | 同时满足：`--apply` **且** `ALLOW_TICKTICK_SYNC=1` |
| 清单名 | 默认 `固定债务与还款日`（与 bank-bill-extractor 的「信用卡还款」**分开**） |
| 内容 | 信用卡固定还款日（可附带 bills 本期金额）+ 贷款固定月供 |

**在用户明确说「授权同步滴答 / 写入滴答清单」之前，AI 不得执行 `--apply`。**

### 7.2 预览（随时可跑，安全）

```powershell
cd "K:\Trae CN\credit-card-planner"
python scripts/ticktick_sync_planner.py
# 只看贷款：
python scripts/ticktick_sync_planner.py --loans-only
# 只看卡：
python scripts/ticktick_sync_planner.py --cards-only
# 未来 3 个月：
python scripts/ticktick_sync_planner.py --months 3
```

### 7.3 授权后写入（用户一声令下再执行）

```powershell
cd "K:\Trae CN\credit-card-planner"
$env:ALLOW_TICKTICK_SYNC = "1"
$env:TICKTICK_API_KEY = "滴答 OpenAPI 的 Bearer Token（dida365）"
python scripts/ticktick_sync_planner.py --apply
```

可选参数：

| 参数 | 含义 |
|------|------|
| `--project "名字"` | 清单项目名 |
| `--months N` | 生成未来 N 个自然月 |
| `--loans-only` | 仅固定债务 |
| `--cards-only` | 仅信用卡还款日 |
| `--api-key xxx` | 临时覆盖环境变量 |

去重：同清单下相同 `title` 已存在则跳过。

### 7.4 API 说明

- 国内滴答 OpenAPI 基址：`https://api.dida365.com/open/v1`  
- 鉴权：`Authorization: Bearer <TICKTICK_API_KEY>`  
- 也可复用 `K:\Trae CN\R BANK\ticktick_api.py`（若存在）  
- **禁止**把 Key 提交进 Git

### 7.5 用户授权话术（给 AI）

用户说类似下面任一句，才允许 `--apply`：

- 「授权同步滴答清单」  
- 「把固定还款写进滴答」  
- 「执行 ticktick --apply」  

否则只允许 dry-run。

---

## 8. 与 bank-bill-extractor 的关系

| | bank-bill-extractor | credit-card-planner（本仓库） |
|--|---------------------|-------------------------------|
| 仓库 | vrbtc/bank-bill-extractor | vrbtc/credit-card-planner |
| Pages | 账单金额仪表盘 | 现金流日历 · 刷卡规划 |
| 邮箱提取 | 主流程 generate_dashboard | `refresh_bills_from_email.py` 复用其代码 |
| 滴答 | 按**本期账单金额**同步「信用卡还款」 | 按**固定还款日/月供**同步「固定债务与还款日」 |
| 改代码原则 | 互不覆盖对方 `index.html` | 独立仓库独立部署 |

---

## 9. 给 AI 智能体的操作清单

### 9.1 只改展示数据

1. 改 `data.js`（补充额度/账单日/贷款）  
2. 或跑 `refresh_bills_from_email.py` 更新 `bills.json`  
3. `git commit` + `git push origin master`  
4. 打开 Pages 强制刷新验证  

### 9.2 用户要同步滴答

1. **先** dry-run：`python scripts/ticktick_sync_planner.py`  
2. 把将创建的任务列表给用户确认  
3. 用户明确授权后：设 `ALLOW_TICKTICK_SYNC=1` 与 Key，再 `--apply`  
4. 汇报新建/跳过数量  

### 9.3 禁止事项

- 未授权不得 `--apply` 写滴答  
- 不得把 Token / 邮箱密码写入仓库  
- 不得修改 `bank-bill-extractor` 的 `gh-pages/index.html` 来塞本功能（应保持分离）  
- 不得用人工补充覆盖邮件已有还款日/金额  

---

## 10. 依赖

- **前端**：无构建；现代浏览器即可  
- **刷新邮件 / 滴答脚本**：Python 3.10+，`requests`（与 R BANK 的 `requirements.txt` 一致即可）  
- **邮件刷新**：依赖本机 R BANK 项目与 `config.json`  

```powershell
pip install requests
```

---

## 11. 安全

- 密钥只用环境变量或本机未入库的 `config.json`  
- 曾在聊天中发过的 Token 应到对应平台**撤销并轮换**  
- `bills.json` 含账单金额，仓库若 public 请知悉隐私风险  

---

## 12. 版本与维护

| 项 | 值 |
|----|-----|
| 页面名 | 现金流日历 · 刷卡规划 |
| 默认分支 | `master` |
| 本地路径（当前机） | `K:\Trae CN\credit-card-planner` |
| 关联邮箱工程 | `K:\Trae CN\R BANK`（bank-bill-extractor） |

**最后同步说明（给后续 AI）**：滴答模块已就绪；用户尚未最终授权写入。授权后执行 §7.3。数据规则见 §3。部署见 §4。

---

_文档与代码同步维护；改行为时请同时更新本 README。_
