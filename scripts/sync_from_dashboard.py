#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 bank-bill-extractor 仪表盘 data.json 同步账单到本仓库 bills.json。

数据源：https://vrbtc.github.io/bank-bill-extractor/data.json
（bank-bill-extractor 的 GitHub Actions 每日自动从邮箱提取，含 8 月等未来账单）

本脚本不读邮箱、不需凭据，纯粹从公开 Pages 拉数据并转换格式。
bank-bill-extractor 已经过滤掉 TickTick 里标记完成的银行，所以本数据也排除已还款项。
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

BJ = timezone(timedelta(hours=8))
SRC_URL = "https://vrbtc.github.io/bank-bill-extractor/data.json"
OUT = Path(__file__).resolve().parent.parent / "bills.json"


def main():
    print(f"Fetching {SRC_URL} ...")
    req = urllib.request.Request(SRC_URL, headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)

    if data.get("extract_error"):
        raise RuntimeError(f"bank-bill-extractor 上次提取出错: {data['extract_error']}")

    now = datetime.now(BJ).strftime("%Y-%m-%d %H:%M:%S")
    src_ts = data.get("generated_at", "?")

    # bank-bill-extractor 的 all_bills 字段与 credit-card-planner 几乎一致
    # 仅需去掉 days_until / status（credit-card-planner 不用这两个字段）
    all_bills = []
    for b in data.get("all_bills", []):
        due = b.get("due_date") or ""
        due_day = b.get("due_day")
        if not due_day and due:
            try:
                due_day = int(due[8:10])
            except Exception:
                due_day = None
        all_bills.append({
            "bank_name": b.get("bank_name") or "",
            "source_label": b.get("source_label") or "",
            "bank": b.get("bank") or b.get("bank_name") or "",
            "amount": float(b.get("amount") or 0),
            "due_date": due,
            "due_day": due_day,
            "statement_date": b.get("statement_date"),
            "statement_day": b.get("statement_day"),
            "credit_limit": b.get("credit_limit"),
            "subjects": b.get("subjects") or [],
        })

    # 按还款日 + 银行名排序
    all_bills.sort(key=lambda x: (x.get("due_date") or "9999", x.get("bank", "")))
    total = round(sum(b["amount"] for b in all_bills), 2)
    planner = {
        "generated_at": now,
        "source": f"synced from bank-bill-extractor data.json (generated {src_ts})",
        "all_bills": all_bills,
        "total_all": total,
    }

    OUT.write_text(json.dumps(planner, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(all_bills)} bills, total {total})")
    print(f"  source: data.json generated {src_ts}")
    for b in all_bills:
        print(f"  {b['due_date']} {b['bank']:20} amt={b['amount']:10.2f} label={b.get('source_label')!r}")


if __name__ == "__main__":
    main()
