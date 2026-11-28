"""Lấy thời gian và quãng đường ĐƯỜNG BỘ giữa mọi cặp điểm trong data/places.csv từ OSRM, ghi data/travel_road.csv.

    python data/build_road_matrix.py

OSRM (router.project-osrm.org, dữ liệu OpenStreetMap) trả thời gian ô tô khi đường thông thoáng. verify.travel_min
nhân thêm hệ số kẹt xe / gửi xe (ROAD_FACTOR, ROAD_EXTRA ở verify.py, hiệu chỉnh theo các chặng Google Maps trong
travel_override.csv). Cặp có trong travel_override.csv vẫn được ưu tiên. Chạy lại khi places.csv thêm điểm.
Chỉ dùng thư viện chuẩn.
"""
from __future__ import annotations

import csv
import datetime
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))
os.environ.setdefault("ALTF4_DATA", "real")

from domain import load_places  # noqa: E402

TABLE = "https://router.project-osrm.org/table/v1/driving/"
OUT = os.path.join(ROOT, "data", "travel_road.csv")


def main() -> int:
    places = list(load_places(os.path.join(ROOT, "data", "places.csv")).values())
    coords = ";".join("%s,%s" % (p.lon, p.lat) for p in places)
    req = urllib.request.Request(TABLE + coords + "?annotations=duration,distance",
                                 headers={"User-Agent": "AltF4-demo/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.loads(r.read())
    if body.get("code") != "Ok":
        print("OSRM lỗi:", body.get("code"), body.get("message"), file=sys.stderr)
        return 1
    today = datetime.date.today().isoformat()
    rows = 0
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["from_id", "to_id", "osrm_min", "km", "source", "checked_on"])
        for i, a in enumerate(places):
            for j, b in enumerate(places):
                dur, dist = body["durations"][i][j], body["distances"][i][j]
                if i == j or dur is None or dist is None:
                    continue
                w.writerow([a.id, b.id, round(dur / 60, 1), round(dist / 1000, 2),
                           "OSRM table (router.project-osrm.org, OpenStreetMap), ô tô, đường thông thoáng", today])
                rows += 1
    print("Đã ghi %s: %d chặng giữa %d điểm" % (os.path.relpath(OUT, ROOT), rows, len(places)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
