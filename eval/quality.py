"""Chỉ số CHẤT LƯỢNG LỊCH — chỉ để báo cáo thêm, KHÔNG thay chuẩn "đạt" đã khóa ở spec.md §7.

Vì sao có file này: 4 metric đã khóa (eval/metric_spec.yaml) đo lịch có KHẢ THI và TRUNG THỰC không
(0 vi phạm, không bịa, nói được "không xếp được", từ chối đúng). Chúng không đo lịch có ĐÁNG ĐI không:
một lịch để trống 4 tiếng hay bắt nhóm ăn 3 bữa vẫn qua cả 4 metric. Xem eval/metric-gaps.md.

    python eval/quality.py eval/run-1.csv                 bảng chỉ số cho các câu trả về lịch
    python eval/quality.py eval/run-1.csv eval/run-2.csv  so hai lượt

Chỉ đọc file lượt chạy, không ghi gì. Ràng buộc lấy từ c= của câu (giống grader), không dùng ràng buộc model tự hiểu.
"""
from __future__ import annotations

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))
sys.path.insert(0, os.path.join(ROOT, "eval"))

import grade  # noqa: E402  (dùng chung cách đọc output và c= với grader)
import tools  # noqa: E402
import verify as core  # noqa: E402

BIG_GAP = 60  # phút chờ (đã trừ di chuyển) coi là "lịch hổng"


def row_quality(row, data):
    obj, err, _ = grade.split_output(row.get("output", ""))
    if obj is None or obj.get("status") != "plan":
        return None
    plan = grade.to_plan(obj.get("stops"))
    _, c = grade.parse_criterion(row.get("pass_criterion", ""))
    if plan is None or c is None or any(s.place_id not in data.places for s in plan.stops):
        return None
    gaps = [max(0, core.idle_min(plan, i, data)) for i in range(1, len(plan.stops))]
    meals = sum(data.places[s.place_id].kind == "an" for s in plan.stops)
    span = c.end - c.start
    busy = sum(s.leave - s.arrive for s in plan.stops)
    total = core.cost(plan, c, data).total
    return {
        "id": row["id"], "stops": len(plan.stops), "idle": sum(gaps), "max_gap": max(gaps, default=0),
        "big_gaps": sum(g > BIG_GAP for g in gaps), "extra_meals": max(0, meals - len(core.required_meals(c))),
        "fill_pct": round(100 * busy / span) if span else 0,
        "budget_pct": round(100 * total / c.budget_total) if c.budget_total else 0,
    }


def summarize(path):
    data = tools.data()
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = [q for q in (row_quality(r, data) for r in csv.DictReader(f)) if q]
    n = len(rows)
    if not n:
        return path, rows, {}
    agg = {
        "số câu có lịch": n,
        "TB số điểm": round(sum(r["stops"] for r in rows) / n, 1),
        "TB phút chết / lịch": round(sum(r["idle"] for r in rows) / n),
        "lịch có khoảng chờ > %d phút" % BIG_GAP: "%d/%d" % (sum(r["big_gaps"] > 0 for r in rows), n),
        "lịch có quán ăn thừa": "%d/%d" % (sum(r["extra_meals"] > 0 for r in rows), n),
        "TB % khung giờ có hoạt động": round(sum(r["fill_pct"] for r in rows) / n),
        "TB % ngân sách dùng": round(sum(r["budget_pct"] for r in rows) / n),
    }
    return path, rows, agg


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    results = [summarize(p) for p in argv]
    for path, rows, _ in results:
        print("\n## %s" % path)
        print("| câu | số điểm | phút chết | chờ dài nhất | quán ăn thừa | % khung có hoạt động | % ngân sách |")
        print("|---|---|---|---|---|---|---|")
        for r in rows:
            print("| %(id)s | %(stops)d | %(idle)d | %(max_gap)d | %(extra_meals)d | %(fill_pct)d%% | %(budget_pct)d%% |" % r)
    keys = list(results[0][2])
    print("\n## Tổng hợp\n| chỉ số | " + " | ".join(os.path.basename(p) for p, _, _ in results) + " |")
    print("|---|" + "---|" * len(results))
    for k in keys:
        print("| %s | %s |" % (k, " | ".join(str(a.get(k, "–")) for _, _, a in results)))
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    sys.exit(main(sys.argv[1:]))
