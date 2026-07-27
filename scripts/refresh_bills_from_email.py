#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 R BANK 邮箱实时提取账单，写入本仓库 bills.json（含额度/账单日/YY）。"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BJ = timezone(timedelta(hours=8))
R_BANK = Path(r"K:\Trae CN\R BANK")
OUT = Path(__file__).resolve().parent.parent / "bills.json"


def main():
    sys.path.insert(0, str(R_BANK))
    from this_month_bills import BillExtractor

    print("Fetching emails...")
    extractor = BillExtractor()
    bills = extractor.fetch_and_extract(limit=80)
    print(f"raw bills: {len(bills)}")

    now = datetime.now(BJ)
    # 同步写回原项目 this_month_bills.json（不改 gh-pages 页面结构）
    raw_path = R_BANK / "this_month_bills.json"
    raw_path.write_text(
        json.dumps(
            {"generated_at": now.strftime("%Y-%m-%d %H:%M:%S"), "bills": bills},
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    today = now.date()
    agg: dict = {}

    for b in bills:
        bank = b.get("bank_name") or ""
        label = (b.get("source_label") or "").strip()
        dues = []
        for d in b.get("due_dates") or []:
            d2 = str(d).replace("/", "-")[:10]
            try:
                datetime.strptime(d2, "%Y-%m-%d")
                dues.append(d2)
            except Exception:
                continue
        if not dues:
            continue

        best = None
        best_score = 10**9
        for d2 in dues:
            dd = datetime.strptime(d2, "%Y-%m-%d").date()
            days = (dd - today).days
            if days < -21:
                continue
            # 优先未过期，其次最近
            score = days if days >= 0 else 1000 + abs(days)
            if score < best_score:
                best_score = score
                best = d2
        if not best:
            best = sorted(dues)[-1]

        amt = 0.0
        for a in b.get("amounts") or []:
            cur = a.get("currency") or "CNY"
            if cur in ("CNY", "RMB", ""):
                amt += float(a.get("value") or 0)

        stmt_dates = [str(s).replace("/", "-")[:10] for s in (b.get("statement_dates") or [])]
        stmt_day = b.get("statement_day")
        if not stmt_day and stmt_dates:
            try:
                stmt_day = int(stmt_dates[0][8:10])
            except Exception:
                pass
        due_day = int(best[8:10])
        limit = b.get("credit_limit")
        subject = b.get("subject") or ""

        # 同银行同 label 同还款日合并金额；不同还款日分开（如招行主卡/分期）
        key = f"{bank}|{label}|{best}"
        if key not in agg:
            agg[key] = {
                "bank_name": bank,
                "source_label": label,
                "bank": f"{bank} ({label})" if label else bank,
                "amount": amt,
                "due_date": best,
                "due_day": due_day,
                "statement_date": stmt_dates[0] if stmt_dates else None,
                "statement_day": stmt_day,
                "credit_limit": limit,
                "subjects": [subject] if subject else [],
            }
        else:
            prev = agg[key]
            prev["amount"] = round(prev["amount"] + amt, 2)
            if limit and (not prev.get("credit_limit") or float(limit) > float(prev["credit_limit"])):
                prev["credit_limit"] = limit
            if stmt_dates and not prev.get("statement_date"):
                prev["statement_date"] = stmt_dates[0]
            if stmt_day and not prev.get("statement_day"):
                prev["statement_day"] = stmt_day
            if subject:
                prev["subjects"].append(subject)

    # 同卡多还款日时：仅补全额度与「每月账单日数字」；不跨期复制具体 statement_date
    by_card: dict = {}
    for item in agg.values():
        ck = f"{item['bank_name']}|{item['source_label']}"
        by_card.setdefault(ck, []).append(item)
    for items in by_card.values():
        best_limit = max((float(i["credit_limit"]) for i in items if i.get("credit_limit")), default=None)
        # 优先用较新一期的 statement_day
        items_sorted = sorted(items, key=lambda x: x.get("due_date") or "", reverse=True)
        best_stmt_day = next((i.get("statement_day") for i in items_sorted if i.get("statement_day")), None)
        for i in items:
            if best_limit and not i.get("credit_limit"):
                i["credit_limit"] = best_limit
            if best_stmt_day and not i.get("statement_day"):
                i["statement_day"] = best_stmt_day

    all_bills = sorted(agg.values(), key=lambda x: (x.get("due_date") or "9999", x.get("bank", "")))
    planner = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "live email extract",
        "all_bills": all_bills,
        "total_all": round(sum(float(b.get("amount") or 0) for b in all_bills), 2),
    }
    OUT.write_text(json.dumps(planner, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(all_bills)} bills, total {planner['total_all']})")
    for b in all_bills:
        print(
            f"{b['due_date']} {b['bank']:18} "
            f"amt={b['amount']:10.2f} limit={b.get('credit_limit')} "
            f"stmt={b.get('statement_date') or b.get('statement_day')} label={b.get('source_label')!r}"
        )


if __name__ == "__main__":
    main()
