/**
 * 现金流日历 · 刷卡规划 — 配置
 *
 * ★ 合并规则（务必遵守）：
 *   1. 邮件有的字段 → 一律以邮件为准（还款日、账单日、金额、已解析到的额度…）
 *   2. 邮件没有的字段 → 用本文件「人工补充」（如下方 credit_limit、现账单日）
 *
 * source_label = "YY" 的卡会标注 YY
 */
window.PLANNER_DATA = {
  updated_at: "2026-07-27",
  principal_as_of: "2026-07-27",
  timezone: "Asia/Shanghai",
  bill_sources: [
    "./bills.json",
    "https://vrbtc.github.io/bank-bill-extractor/data.json"
  ],

  /**
   * cards：人工补充 + 展示元数据
   * credit_limit / statement_day：仅当邮件未解析到时使用
   * due_day：邮件未解析到还款日时使用
   * 总额度合计 651200（11 张主卡，不含长安 YY）
   */
  cards: [
    { name: "工商银行", last4: "9889", statement_day: 1,  due_day: 15, credit_limit: 80000, short: "工", color: "#c41e3a", enabled: true },
    { name: "浦发银行", last4: "8182", statement_day: 4,  due_day: 24, credit_limit: 52500, short: "浦", color: "#003b8e", enabled: true },
    { name: "邮储银行", last4: "6983", statement_day: 6,  due_day: 24, credit_limit: 50000, short: "邮", color: "#007a3d", enabled: true },
    { name: "兴业银行", last4: "1561", statement_day: 10, due_day: 29, credit_limit: 75700, short: "兴", color: "#004b87", enabled: true },
    { name: "光大银行", last4: "8685", statement_day: 12, due_day: 31, credit_limit: 96000, short: "光", color: "#6b2d8b", enabled: true },
    { name: "平安银行", last4: "9918", statement_day: 13, due_day: 1,  credit_limit: 10000, short: "平", color: "#f60", enabled: true },
    { name: "广发银行", last4: "8948", statement_day: 17, due_day: 6,  credit_limit: 50000, short: "广", color: "#e60012", enabled: true },
    { name: "招商银行", last4: "6478", statement_day: 18, due_day: 5,  credit_limit: 45000, short: "招", color: "#e60012", enabled: true },
    { name: "交通银行", last4: "8940", statement_day: 21, due_day: 15, credit_limit: 58000, short: "交", color: "#003b70", enabled: true },
    { name: "建设银行", last4: "2504", statement_day: 26, due_day: 15, credit_limit: 80000, short: "建", color: "#0066b3", enabled: true },
    { name: "民生银行", last4: "2821", statement_day: 27, due_day: 16, credit_limit: 54000, short: "民", color: "#00a0e9", enabled: true },
    { name: "长安银行", last4: "",    statement_day: 20, due_day: 15, credit_limit: null,  short: "长", color: "#0d9488", source_label: "YY", enabled: true }
  ],

  /**
   * rate_annual: 年化利率，写 0.031 或 3.1 均可（3.1 表示 3.1%）
   * principal_as_of: 可选，覆盖全局快照日
   * amortize: epi=等额本息 | installment=每期近似全扣本金
   */
  loans: [
    { category: "房贷",       bank: "建行", monthly: 3014, due_day: 15, principal_total: 670000, principal_left: 579406.84, principal_as_of: "2026-07-27", amortize: "epi", rate_annual: 3.2, enabled: true },
    { category: "车贷",       bank: "招行", monthly: 2834, due_day: 28, principal_total: 170000, principal_left: 124666, principal_as_of: "2026-01-09", amortize: "epi", rate_annual: 4.5, enabled: true },
    { category: "邮储贷款",   bank: "邮储", monthly: 2271, due_day: 16, principal_total: 125000, principal_left: 120334, principal_as_of: "2026-01-09", amortize: "epi", rate_annual: 4.0, enabled: true },
    { category: "融E借",      bank: "工行", monthly: 850,  due_day: 19, principal_total: 300000, principal_left: 300000, principal_as_of: "2026-01-09", amortize: "epi", rate_annual: 5.5, enabled: true },
    { category: "惠民贷",     bank: "交行", monthly: 523,  due_day: 15, principal_total: 150000, principal_left: 100693, principal_as_of: "2026-01-09", amortize: "epi", rate_annual: 4.5, enabled: true },
    { category: "光速贷",     bank: "光大", monthly: 333,  due_day: 20, principal_total: 116000, principal_left: 115887, principal_as_of: "2026-01-09", amortize: "epi", rate_annual: 6.0, enabled: true },
    { category: "招行分期卡", bank: "招行", monthly: 2795, due_day: 6,  principal_total: 64798,  principal_left: 59548,  principal_as_of: "2026-01-09", amortize: "installment", note: "分期月供近似全本金", enabled: true }
  ]
};
