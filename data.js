/**
 * 信用卡 & 长期贷款配置
 * ------------------------------------------------
 * 修改本文件后刷新页面即可生效（GitHub Pages 部署后需重新推送）。
 *
 * cards 字段说明：
 *   name          - 卡片名称
 *   statement_day - 账单日（每月几号出账，1-31）
 *   due_day       - 还款日（每月几号到期，1-31）
 *   note          - 备注（可选）
 *   enabled       - 是否参与「今天刷哪张最划算」推荐
 *
 * loans 字段说明：
 *   name          - 贷款/债务名称
 *   amount        - 每月固定还款金额（元）
 *   due_day       - 每月还款日（1-31）
 *   note          - 备注（可选）
 *   enabled       - 是否显示
 *
 * ⚠️ statement_day 目前根据账单邮件发送日估算，请用你实际的账单日覆盖。
 *    due_day 根据近期电子账单还款日推断。
 */
window.PLANNER_DATA = {
  updated_at: "2026-07-27",
  timezone: "Asia/Shanghai",

  cards: [
    // statement_day 为估算值（≈账单邮件发送日），请按真实账单日修正
    { name: "浦发银行", statement_day: 5,  due_day: 24, note: "账单日待确认", enabled: true },
    { name: "邮储银行", statement_day: 7,  due_day: 27, note: "账单日待确认", enabled: true },
    { name: "招商银行", statement_day: 19, due_day: 6,  note: "含分期/e招贷等同日还款", enabled: true },
    { name: "兴业银行", statement_day: 11, due_day: 30, note: "账单日待确认", enabled: true },
    { name: "光大银行", statement_day: 14, due_day: 31, note: "账单日待确认", enabled: true },
    { name: "平安银行", statement_day: 14, due_day: 1,  note: "账单日待确认", enabled: true },
    { name: "广发银行", statement_day: 18, due_day: 6,  note: "账单日待确认", enabled: true },
    { name: "交通银行", statement_day: 22, due_day: 15, note: "账单日待确认", enabled: true },
    { name: "工商银行", statement_day: 2,  due_day: 19, note: "账单日待确认", enabled: true },
    { name: "民生银行", statement_day: 28, due_day: 17, note: "账单日待确认", enabled: true },
    { name: "建设银行", statement_day: 28, due_day: 15, note: "账单日待确认", enabled: true },
    { name: "长安银行 (YY)", statement_day: 22, due_day: 15, note: "YY 邮箱", enabled: true }
  ],

  /**
   * 长期贷款 / 固定月供 —— 请按你的真实情况填写后推送更新
   * 示例已注释，取消注释并改数字即可
   */
  loans: [
    // { name: "房贷-XX银行", amount: 8500, due_day: 10, note: "等额本息", enabled: true },
    // { name: "车贷", amount: 3200, due_day: 18, note: "", enabled: true },
    // { name: "消费分期固定", amount: 1500, due_day: 6, note: "招行", enabled: true }
  ]
};
