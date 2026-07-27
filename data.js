/**
 * 信用卡 & 长期贷款配置（真实数据）
 * 修改后推送即可更新 GitHub Pages。
 *
 * cards:
 *   name, last4, statement_day(出账/账单日), due_day(还款日), short, color, enabled
 * loans:
 *   category, bank, monthly, due_day, principal_total, principal_left, note, enabled
 */
window.PLANNER_DATA = {
  updated_at: "2026-07-27",
  principal_as_of: "2026-01-09",
  timezone: "Asia/Shanghai",

  cards: [
    { name: "工商银行", last4: "9889", statement_day: 1,  due_day: 15, short: "工", color: "#c41e3a", enabled: true },
    { name: "浦发银行", last4: "8182", statement_day: 4,  due_day: 24, short: "浦", color: "#003b8e", enabled: true },
    { name: "邮储银行", last4: "6983", statement_day: 6,  due_day: 24, short: "邮", color: "#007a3d", enabled: true },
    { name: "兴业银行", last4: "1561", statement_day: 10, due_day: 29, short: "兴", color: "#004b87", enabled: true },
    { name: "光大银行", last4: "8685", statement_day: 12, due_day: 31, short: "光", color: "#6b2d8b", enabled: true },
    { name: "平安银行", last4: "9918", statement_day: 13, due_day: 1,  short: "平", color: "#f60", enabled: true },
    { name: "广发银行", last4: "8948", statement_day: 17, due_day: 6,  short: "广", color: "#e60012", enabled: true },
    { name: "招商银行", last4: "6478", statement_day: 18, due_day: 5,  short: "招", color: "#e60012", enabled: true },
    { name: "交通银行", last4: "8940", statement_day: 21, due_day: 15, short: "交", color: "#003b70", enabled: true },
    { name: "建设银行", last4: "2504", statement_day: 26, due_day: 15, short: "建", color: "#0066b3", enabled: true },
    { name: "民生银行", last4: "2821", statement_day: 27, due_day: 16, short: "民", color: "#00a0e9", enabled: true }
  ],

  loans: [
    { category: "房贷",     bank: "建行", monthly: 3018, due_day: 15, principal_total: 670000, principal_left: 589573, note: "", enabled: true },
    { category: "车贷",     bank: "招行", monthly: 2834, due_day: 28, principal_total: 170000, principal_left: 124666, note: "", enabled: true },
    { category: "邮储贷款", bank: "邮储", monthly: 2271, due_day: 16, principal_total: 125000, principal_left: 120334, note: "", enabled: true },
    { category: "融E借",    bank: "工行", monthly: 850,  due_day: 19, principal_total: 300000, principal_left: 300000, note: "", enabled: true },
    { category: "惠民贷",   bank: "交行", monthly: 523,  due_day: 15, principal_total: 150000, principal_left: 100693, note: "", enabled: true },
    { category: "光速贷",   bank: "光大", monthly: 333,  due_day: 20, principal_total: 116000, principal_left: 115887, note: "", enabled: true },
    { category: "招行分期卡", bank: "招行", monthly: 2795, due_day: 6,  principal_total: 64798,  principal_left: 59548,  note: "分期卡月供", enabled: true }
  ]
};
