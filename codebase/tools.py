"""Công cụ của bài toán — Đức giữ file này. Mỗi công cụ một hàm có @tool, đều CHỈ ĐỌC.

Đây là lớp mỏng bọc lõi thuần ở verify.py, để trace ghi mỗi lần luồng chính gọi công cụ.
Lõi gọi thẳng nhau, không qua @tool, nên một lần xếp lịch thử nhiều hoán vị không làm phình trace.

Dữ liệu: data/places.csv, data/transport_rates.csv (bắt buộc khi đã có places.csv), data/travel_override.csv (tuỳ chọn).
Chưa có data/places.csv thì dùng bộ dữ liệu thử synthetic ở tests/*_fixture.csv và output ghi rõ điều đó.
Đặt biến môi trường ALTF4_DATA=fixture để luôn dùng bộ thử (test làm vậy).
"""
from __future__ import annotations

import os

import verify as core
from domain import (Constraints, DataError, Place, Plan, Relax, Violation, load_overrides, load_places, load_prefs,
                    load_rates, load_road)
from tracing import tool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = {"places": "data/places.csv", "travel": "data/travel_override.csv", "rates": "data/transport_rates.csv",
        "road": "data/travel_road.csv", "prefs": "data/visit_prefs.csv"}
FIXTURE = {"places": "tests/places_fixture.csv", "travel": "tests/travel_override_fixture.csv",
           "rates": "tests/transport_rates_fixture.csv"}

_loaded: dict = {}


def _paths() -> dict:
    use_fixture = os.environ.get("ALTF4_DATA") == "fixture" or not os.path.exists(os.path.join(ROOT, REAL["places"]))
    return FIXTURE if use_fixture else REAL


def data() -> core.Data:
    """Nạp dữ liệu một lần mỗi tiến trình (đổi bộ dữ liệu thì nạp lại)."""
    paths = _paths()
    if _loaded.get("paths") is not paths:
        full = {k: os.path.join(ROOT, v) for k, v in paths.items()}
        places = load_places(full["places"])
        if not os.path.exists(full["rates"]):
            raise DataError("thiếu %s: ngân sách gồm cả tiền đi lại nên cần đơn giá" % paths["rates"])
        overrides = load_overrides(full["travel"], places) if os.path.exists(full["travel"]) else {}
        road = load_road(full["road"], places) if "road" in full and os.path.exists(full["road"]) else {}
        prefs = load_prefs(full["prefs"], places) if "prefs" in full and os.path.exists(full["prefs"]) else {}
        _loaded.update(paths=paths, data=core.Data(places, overrides, load_rates(full["rates"]), road, prefs))
    return _loaded["data"]


def source() -> str:
    """Tên file địa điểm đang dùng, để output ghi rõ khi đang chạy bằng dữ liệu thử."""
    return _paths()["places"]


def using_fixture() -> bool:
    return _paths() is FIXTURE


@tool
def shortlist(c: Constraints) -> list[Place]:
    """shortlist · input: Constraints · output: ≤ 15 Place đã lọc ngày nghỉ, tag tránh, món kiêng, giá một điểm,
    xếp theo độ khớp sở thích · không tác động ra ngoài."""
    return core.shortlist(c, data())


@tool
def get_place(place_id: str) -> Place | None:
    """get_place · input: place_id · output: dòng dữ liệu (giờ, giá, tag, nguồn, ngày kiểm) hoặc None ·
    không tác động ra ngoài."""
    return data().places.get(place_id)


@tool
def travel_min(a_id: str, b_id: str) -> int:
    """travel_min · input: 2 place_id · output: số phút di chuyển (ước tính từ tọa độ, trừ cặp có trong
    travel_override.csv) · không tác động ra ngoài."""
    return core.travel_min(a_id, b_id, data())


@tool
def transport_cost(a_id: str, b_id: str, mode: str, people: int) -> int:
    """transport_cost · input: 2 place_id, phương tiện (grab | xe_may), số người · output: tiền đi chặng đó
    cho cả nhóm, VND (ước tính) · không tác động ra ngoài."""
    return core.transport_cost(a_id, b_id, mode, people, data())


@tool
def verify(plan: Plan, c: Constraints) -> list[Violation]:
    """verify · input: Plan + Constraints · output: danh sách vi phạm ràng buộc cứng, rỗng = hợp lệ ·
    không tác động ra ngoài."""
    return core.verify(plan, c, data())


@tool
def relax_options(c: Constraints) -> list[Relax]:
    """relax_options · input: Constraints · output: 1–3 cách nới (bỏ điểm, tăng ngân sách, kéo dài giờ),
    mỗi cách kèm lịch đã qua verify · không tác động ra ngoài."""
    return core.relax_options(c, data())
