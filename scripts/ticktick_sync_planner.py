#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
刷卡规划 → 滴答清单提醒（独立脚本，默认 dry-run）

功能：
1. 根据 data.js 中的信用卡还款日，生成本月/下月还款提醒任务
2. 根据长期贷款 loans，生成每月固定债务提醒
3. 默认 --dry-run 只打印计划，不调用 API
4. 显式传入 --apply 且环境变量 ALLOW_TICKTICK_SYNC=1 时才会真正写入

与 bank-bill-extractor 的账单同步完全独立，使用单独清单名，避免冲突。

用法：
  # 预览（安全，不写任何任务）
  python scripts/ticktick_sync_planner.py

  # 真正同步（需你授权）
  set ALLOW_TICKTICK_SYNC=1
  set TICKTICK_API_KEY=你的key
  python scripts/ticktick_sync_planner.py --apply

可选：
  --project "固定债务与还款日"   # 清单名称
  --months 2                   # 生成未来几个月
  --data ../data.js            # 配置文件路径
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# 允许从本仓库 scripts/ 直接运行；若同机存在 bank-bill-extractor 的 ticktick_api 可复用
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
BJ = timezone(timedelta(hours=8))


def _load_ticktick_api():
    """优先用环境/本地封装；找不到则用内联最小实现。"""
    # 1) 同目录旁的 ticktick_api.py
    local = SCRIPT_DIR / "ticktick_api.py"
    if local.exists():
        sys.path.insert(0, str(SCRIPT_DIR))
        from ticktick_api import TickTickAPI  # type: ignore
        return TickTickAPI

    # 2) 旧项目路径（可选）
    legacy = Path(r"K:\Trae CN\R BANK\ticktick_api.py")
    if legacy.exists():
        sys.path.insert(0, str(legacy.parent))
        from ticktick_api import TickTickAPI  # type: ignore
        return TickTickAPI

    # 3) 最小内联客户端
    import requests

    class TickTickAPI:  # type: ignore
        BASE = "https://api.dida365.com/open/v1"

        def __init__(self, api_key=None):
            self.api_key = (api_key or os.environ.get("TICKTICK_API_KEY", "")).strip()
            if not self.api_key:
                raise ValueError("TICKTICK_API_KEY 未设置")
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

        def get_projects(self):
            r = self.session.get(f"{self.BASE}/project")
            r.raise_for_status()
            return r.json()

        def create_project(self, name, kind="TASK", view_mode="list"):
            r = self.session.post(
                f"{self.BASE}/project",
                json={"name": name, "kind": kind, "viewMode": view_mode},
            )
            r.raise_for_status()
            return r.json()

        def get_project_tasks(self, project_id):
            r = self.session.get(f"{self.BASE}/project/{project_id}/data")
            r.raise_for_status()
            data = r.json()
            return data.get("tasks", data if isinstance(data, list) else [])

        def create_task(self, project_id, title, content="", due_date=None,
                        due_hour=11, priority=1, reminders=None, **_):
            # due_date: "YYYY-MM-DD" 北京时间 → UTC
            body = {
                "projectId": project_id,
                "title": title,
                "content": content or "",
                "priority": priority,
                "timeZone": "Asia/Shanghai",
                "isAllDay": False,
            }
            if due_date:
                y, m, d = map(int, due_date.split("-"))
                bj = datetime(y, m, d, due_hour, 0, 0, tzinfo=BJ)
                utc = bj.astimezone(timezone.utc)
                body["dueDate"] = utc.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
            if reminders:
                body["reminders"] = reminders
            r = self.session.post(f"{self.BASE}/task", json=body)
            r.raise_for_status()
            return r.json()

    return TickTickAPI


def parse_data_js(path: Path) -> dict:
    """从 data.js 提取 window.PLANNER_DATA = {...}"""
    text = path.read_text(encoding="utf-8")
    # 去掉块注释与行注释（足够应对我们的 data.js）
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*?$", "", text, flags=re.M)
    m = re.search(r"window\.PLANNER_DATA\s*=\s*(\{.*\})\s*;?", text, re.S)
    if not m:
        raise ValueError(f"无法在 {path} 中解析 PLANNER_DATA")
    raw = m.group(1)
    # JS 对象 → JSON：给未加引号的 key 加引号；true/false 已兼容
    raw = re.sub(r"(\w+)\s*:", r'"\1":', raw)
    raw = raw.replace("'", '"')
    # 尾逗号
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)
    return json.loads(raw)


def clamp_day(year: int, month: int, day: int) -> date:
    last = monthrange(year, month)[1]
    return date(year, month, min(max(1, day), last))


def iter_months(start: date, count: int):
    y, m = start.year, start.month
    for _ in range(count):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def build_tasks(data: dict, months: int = 2) -> list[dict]:
    """生成待创建任务列表（不调用 API）。"""
    today = datetime.now(BJ).date()
    tasks = []

    cards = [c for c in data.get("cards", []) if c.get("enabled", True)]
    loans = [l for l in data.get("loans", []) if l.get("enabled", True)]

    for y, m in iter_months(today.replace(day=1), months):
        # 信用卡还款日提醒（不含金额，金额由账单系统负责）
        for c in cards:
            d = clamp_day(y, m, int(c["due_day"]))
            if d < today:
                continue
            days_until = (d - today).days
            priority = 5 if days_until <= 3 else 3 if days_until <= 7 else 1
            tasks.append({
                "title": f"💳 {c['name']} 还款日",
                "content": (
                    f"固定还款日提醒（刷卡规划）\n"
                    f"账单日：每月 {c.get('statement_day')} 日\n"
                    f"还款日：{d.isoformat()}\n"
                    f"备注：{c.get('note') or '—'}"
                ),
                "due_date": d.isoformat(),
                "priority": priority,
                "reminders": ["TRIGGER:-PT18H", "TRIGGER:PT0M"] if days_until <= 3 else ["TRIGGER:-PT18H"],
                "kind": "card",
            })

        for loan in loans:
            d = clamp_day(y, m, int(loan["due_day"]))
            if d < today:
                continue
            days_until = (d - today).days
            amount = float(loan.get("amount") or 0)
            priority = 5 if days_until <= 3 else 3 if days_until <= 7 else 1
            tasks.append({
                "title": f"💰 {loan['name']} {amount:.2f} 元",
                "content": (
                    f"固定债务月供\n"
                    f"金额：¥{amount:,.2f}\n"
                    f"还款日：{d.isoformat()}\n"
                    f"备注：{loan.get('note') or '—'}"
                ),
                "due_date": d.isoformat(),
                "priority": priority,
                "reminders": ["TRIGGER:-P1D", "TRIGGER:-PT18H"],
                "kind": "loan",
            })

    # 按日期排序
    tasks.sort(key=lambda t: (t["due_date"], t["title"]))
    return tasks


def ensure_project(api, name: str) -> str:
    projects = api.get_projects()
    for p in projects:
        if p.get("name") == name:
            return p["id"]
    created = api.create_project(name)
    return created["id"] if isinstance(created, dict) else created


def existing_titles(api, project_id: str) -> set[str]:
    try:
        tasks = api.get_project_tasks(project_id)
    except Exception:
        return set()
    titles = set()
    for t in tasks or []:
        if isinstance(t, dict) and t.get("title"):
            titles.add(t["title"])
    return titles


def main():
    parser = argparse.ArgumentParser(description="刷卡规划 → 滴答清单（默认 dry-run）")
    parser.add_argument("--data", default=str(ROOT / "data.js"), help="data.js 路径")
    parser.add_argument("--project", default="固定债务与还款日", help="滴答清单项目名")
    parser.add_argument("--months", type=int, default=2, help="生成未来几个月")
    parser.add_argument("--apply", action="store_true", help="真正写入（需 ALLOW_TICKTICK_SYNC=1）")
    parser.add_argument("--api-key", default="", help="可选，覆盖环境变量")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ 找不到配置：{data_path}")
        sys.exit(1)

    data = parse_data_js(data_path)
    tasks = build_tasks(data, months=args.months)

    print(f"📅 将生成 {len(tasks)} 条提醒（未来 {args.months} 个月）")
    print("-" * 60)
    for t in tasks:
        print(f"  [{t['due_date']}] {t['title']}  (P{t['priority']})")
    print("-" * 60)

    if not args.apply:
        print("🔍 dry-run 模式：未写入滴答清单。")
        print("   授权同步请执行：")
        print("   set ALLOW_TICKTICK_SYNC=1")
        print("   set TICKTICK_API_KEY=你的key")
        print("   python scripts/ticktick_sync_planner.py --apply")
        return

    if os.environ.get("ALLOW_TICKTICK_SYNC", "").strip() != "1":
        print("❌ 拒绝写入：请先设置环境变量 ALLOW_TICKTICK_SYNC=1 表示你已授权。")
        sys.exit(2)

    TickTickAPI = _load_ticktick_api()
    api = TickTickAPI(api_key=args.api_key or None)
    project_id = ensure_project(api, args.project)
    print(f"✅ 清单：{args.project} ({project_id})")

    known = existing_titles(api, project_id)
    created = skipped = 0
    for t in tasks:
        if t["title"] in known:
            skipped += 1
            continue
        # 兼容不同 create_task 签名
        try:
            api.create_task(
                project_id,
                title=t["title"],
                content=t["content"],
                due_date=t["due_date"],
                due_hour=11,
                priority=t["priority"],
                reminders=t["reminders"],
            )
        except TypeError:
            api.create_task(
                project_id,
                t["title"],
                t["content"],
                t["due_date"],
            )
        created += 1
        known.add(t["title"])
        print(f"  + {t['title']}")

    print(f"\n完成：新建 {created}，跳过已存在 {skipped}")


if __name__ == "__main__":
    main()
