"""Lõi thuần (code, không gọi model, không ghi trace). Đức giữ file này.

Mọi con số tiền, giờ, quãng đường trong output đều do các hàm ở đây tính (docs/design.md mục 4, "mỗi thứ một chủ").
tools.py bọc vài hàm bằng @tool để trace ghi ở cấp luồng chính; trong lõi gọi thẳng nhau, không qua @tool.

travel_min và transport_cost là ƯỚC TÍNH từ tọa độ (đường chim bay × hệ số đường vòng), không phải số đo thật,
trừ cặp điểm có trong data/travel_override.csv.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from itertools import combinations, permutations

from domain import (FAR_CLUSTERS, Constraints, Place, Plan, Rate, Relax, Stop, Violation, fmt)

SPEED_KMH = 25          # tốc độ đô thị ước tính
DETOUR = 1.3            # hệ số đường vòng so với đường chim bay
MIN_LEG_MIN = 5         # chặng ngắn nhất (gửi xe, đi bộ ra xe)
MAX_STOPS = 6
LUNCH = (11 * 60, 14 * 60)
DINNER = (17 * 60, 20 * 60)
MEAL_MIN_OVERLAP = 90   # khung giờ giao khung bữa từ 90 phút thì bắt buộc có bữa đó
SEATS = {"grab": 4, "xe_may": 2}
MEAL_SHORTLIST = 6


@dataclass(frozen=True)
class Data:
    places: dict[str, Place]
    overrides: dict[tuple[str, str], int]
    rates: dict[str, Rate]


@dataclass(frozen=True)
class Cost:
    tickets: tuple[int, ...]     # tiền vé / ăn từng điểm, theo thứ tự stops
    legs: tuple[int, ...]        # tiền đi lại từng chặng giữa hai điểm liền nhau
    daily: int                   # tiền thuê xe theo ngày (xe_may), 0 với grab

    @property
    def transport(self) -> int:
        return sum(self.legs) + self.daily

    @property
    def total(self) -> int:
        return sum(self.tickets) + self.transport


# ---------------------------------------------------------------- di chuyển

def road_km(a: Place, b: Place) -> float:
    r = 6371.0
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp, dl = p2 - p1, math.radians(b.lon - a.lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h)) * DETOUR


def travel_min(a_id: str, b_id: str, data: Data) -> int:
    if a_id == b_id:
        return 0
    if (a_id, b_id) in data.overrides:
        return data.overrides[(a_id, b_id)]
    km = road_km(data.places[a_id], data.places[b_id])
    return max(MIN_LEG_MIN, math.ceil(km / SPEED_KMH * 60))


def _vehicles(mode: str, people: int) -> int:
    return max(1, math.ceil(people / SEATS[mode]))


def _rate(mode: str, data: Data) -> Rate:
    if mode not in data.rates:
        raise KeyError("thiếu đơn giá cho phương tiện %r trong transport_rates.csv" % mode)
    return data.rates[mode]


def transport_cost(a_id: str, b_id: str, mode: str, people: int, data: Data) -> int:
    """Tiền đi một chặng cho cả nhóm, làm tròn lên nghìn đồng. Xe máy thuê theo ngày nên chặng = 0."""
    if a_id == b_id or mode == "xe_may":
        return 0
    rate = _rate(mode, data)
    km = road_km(data.places[a_id], data.places[b_id])
    one = rate.base_vnd + rate.per_km_vnd * km
    return int(math.ceil(one * _vehicles(mode, people) / 1000) * 1000)


def daily_transport(mode: str, people: int, data: Data) -> int:
    return _rate(mode, data).per_day_vnd * _vehicles(mode, people) if mode == "xe_may" else 0


def ticket(p: Place, c: Constraints) -> int:
    return p.price_pp * (c.people if p.price_basis == "moi_nguoi" else 1)


def cost(plan: Plan, c: Constraints, data: Data) -> Cost:
    known = [s.place_id for s in plan.stops if s.place_id in data.places]
    tickets = tuple(ticket(data.places[i], c) for i in known)
    legs = tuple(transport_cost(a, b, c.transport, c.people, data) for a, b in zip(known, known[1:]))
    return Cost(tickets, legs, daily_transport(c.transport, c.people, data) if known else 0)


# ---------------------------------------------------------------- kiểm

def required_meals(c: Constraints) -> tuple[tuple[int, int], ...]:
    def overlap(band):
        return min(c.end, band[1]) - max(c.start, band[0])
    return tuple(b for b in (LUNCH, DINNER) if overlap(b) >= MEAL_MIN_OVERLAP)


def serves(p: Place, band) -> bool:
    """Quán p có thể làm bữa trong khung band (đến trong khung bữa, ngồi đủ visit_min trong giờ mở)."""
    return p.kind == "an" and any(max(ws, band[0]) < band[1] and max(ws, band[0]) + p.visit_min <= we
                                  for ws, we in p.open_windows)


def _meal_for(band, plan: Plan, data: Data) -> bool:
    return any(s.place_id in data.places and data.places[s.place_id].kind == "an"
               and band[0] <= s.arrive < band[1] for s in plan.stops)


def verify(plan: Plan, c: Constraints, data: Data) -> list[Violation]:
    """Trả mọi vi phạm ràng buộc cứng (bảng luật ở docs/design.md mục 6). Danh sách rỗng = lịch hợp lệ."""
    v: list[Violation] = []
    seen: set[str] = set()
    if len(plan.stops) > MAX_STOPS:
        v.append(Violation("TOO_MANY", None, "%d điểm, tối đa %d" % (len(plan.stops), MAX_STOPS)))
    prev: tuple[int, Stop] | None = None
    for i, s in enumerate(plan.stops):
        if s.place_id in seen:
            v.append(Violation("DUPLICATE", i, s.place_id))
        seen.add(s.place_id)
        p = data.places.get(s.place_id)
        if p is None:
            v.append(Violation("UNKNOWN_PLACE", i, s.place_id))
            continue
        if s.leave - s.arrive < p.visit_min:
            v.append(Violation("TOO_MANY", i, "%s cần ít nhất %d phút" % (p.id, p.visit_min)))
        if s.arrive < c.start or s.leave > c.end:
            v.append(Violation("OUT_OF_WINDOW", i, "%s %s–%s" % (p.id, fmt(s.arrive), fmt(s.leave))))
        if c.day is not None and c.day in p.closed_days:
            v.append(Violation("CLOSED", i, "%s nghỉ ngày này" % p.id))
        elif not any(ws <= s.arrive and s.leave <= we for ws, we in p.open_windows):
            v.append(Violation("CLOSED", i, "%s không mở %s–%s" % (p.id, fmt(s.arrive), fmt(s.leave))))
        if p.id in c.exclude:
            v.append(Violation("AVOID_TAG", i, "%s người dùng đã bỏ khỏi lịch" % p.id))
        bad = set(p.tags) & set(c.avoid)
        if bad:
            v.append(Violation("AVOID_TAG", i, "%s có %s" % (p.id, ",".join(sorted(bad)))))
        if p.kind == "an" and not set(c.diet) <= set(p.tags):
            v.append(Violation("AVOID_TAG", i, "%s thiếu %s" % (p.id, ",".join(sorted(set(c.diet) - set(p.tags))))))
        if prev is not None:
            j, ps = prev
            if s.arrive < ps.leave:
                v.append(Violation("OVERLAP", i, "%s bắt đầu trước khi rời %s" % (p.id, ps.place_id)))
            elif s.arrive < ps.leave + travel_min(ps.place_id, p.id, data):
                v.append(Violation("TRAVEL_GAP", i, "%s → %s cần %d phút" % (
                    ps.place_id, p.id, travel_min(ps.place_id, p.id, data))))
        prev = (i, s)
    for band in required_meals(c):
        if not _meal_for(band, plan, data):
            v.append(Violation("NO_MEAL", None, "thiếu bữa %s–%s" % (fmt(band[0]), fmt(band[1]))))
    if not any(x.code == "UNKNOWN_PLACE" for x in v):
        total = cost(plan, c, data).total
        if total > c.budget_total:
            v.append(Violation("OVER_BUDGET", None, "%d > %d" % (total, c.budget_total)))
    return v


# ---------------------------------------------------------------- xếp lịch bằng code

def _timed(order: tuple[Place, ...], c: Constraints, data: Data) -> Plan | None:
    """Xếp giờ cho một thứ tự cố định: đến sớm nhất có thể, bữa ăn thứ k rơi vào khung bữa thứ k.
    Quán không mở trong khung bữa đang chờ (vd quán chỉ bán sáng) là ghé ăn thêm, không tính là bữa đó."""
    bands = required_meals(c)
    t, prev, meal_k, stops = c.start, None, 0, []
    for p in order:
        earliest = t if prev is None else t + travel_min(prev.id, p.id, data)
        latest = c.end
        if p.kind == "an" and meal_k < len(bands) and serves(p, bands[meal_k]):
            earliest, latest = max(earliest, bands[meal_k][0]), bands[meal_k][1] - 1
            meal_k += 1
        arrive = next((max(earliest, ws) for ws, we in p.open_windows
                       if max(earliest, ws) + p.visit_min <= we and max(earliest, ws) <= latest), None)
        if arrive is None or arrive + p.visit_min > c.end:
            return None
        stops.append(Stop(p.id, arrive, arrive + p.visit_min))
        t, prev = arrive + p.visit_min, p
    return Plan(tuple(stops))


def schedule(ids: tuple[str, ...], c: Constraints, data: Data) -> Plan | None:
    """Tìm thứ tự và giờ cho đúng tập điểm ids sao cho verify() rỗng. Không có thì None.
    Thử mọi hoán vị (≤ 6 điểm → ≤ 720), kéo dài thời gian ở lại (stretch) rồi chọn lịch ít giờ trống nhất:
    tổng thời gian ở các điểm lớn nhất, rồi ít phút đi lại nhất, rồi kết thúc sớm nhất."""
    if not ids or len(ids) > MAX_STOPS or len(set(ids)) != len(ids) or any(i not in data.places for i in ids):
        return None
    places = tuple(data.places[i] for i in ids)
    if sum(p.kind == "an" for p in places) < len(required_meals(c)):
        return None

    def key(p: Plan) -> tuple[int, int, int]:
        stay = sum(s.leave - s.arrive for s in p.stops)
        travel = sum(travel_min(a.place_id, b.place_id, data) for a, b in zip(p.stops, p.stops[1:]))
        return -stay, travel, p.stops[-1].leave
    best: Plan | None = None
    for order in permutations(places):
        plan = _timed(order, c, data)
        if plan is None or verify(plan, c, data):
            continue
        plan = stretch(plan, c, data)
        if best is None or key(plan) < key(best):
            best = plan
    return best


def score(p: Place, c: Constraints) -> int:
    s = 2 * len(set(p.tags) & set(c.like))
    if c.base_cluster and p.cluster == c.base_cluster:
        s += 1
    if p.cluster in FAR_CLUSTERS and p.id not in c.must:
        s -= 2
    if p.kind == "an" and "chay" in p.tags and "chay" not in c.diet:
        s -= 1      # quán chay rẻ nên hay lên đầu khi xếp theo giá; nhóm không ăn chay thì không ưu tiên
    return s


def _rank(c: Constraints):
    return lambda p: (-score(p, c), ticket(p, c), p.id)


def shortlist(c: Constraints, data: Data, limit: int = 15) -> list[Place]:
    """≤ limit ứng viên: điểm bắt buộc + tối đa 6 quán ăn + điểm khác, đã lọc ngày nghỉ, tag tránh, món kiêng, giá 1 điểm."""
    must = [data.places[i] for i in c.must if i in data.places and i not in c.exclude]

    def usable(p: Place) -> bool:
        return (p.id not in c.must and p.id not in c.exclude
                and (c.day is None or c.day not in p.closed_days)
                and not set(p.tags) & set(c.avoid)
                and not (p.kind == "an" and not set(c.diet) <= set(p.tags))
                and ticket(p, c) <= c.budget_total)
    pool = sorted(filter(usable, data.places.values()), key=_rank(c))
    meals = [p for p in pool if p.kind == "an"][:MEAL_SHORTLIST]
    others = [p for p in pool if p.kind != "an"][:max(0, limit - len(must) - len(meals))]
    return must + meals + others


def plan_greedy(c: Constraints, cands: list[Place], data: Data) -> Plan | None:
    """Phương án code: giữ điểm bắt buộc, chọn bữa ăn cần thiết, rồi thêm dần điểm hợp sở thích khi verify vẫn rỗng."""
    must = tuple(i for i in c.must if i in data.places)
    bands = required_meals(c)
    need = max(0, len(bands) - sum(any(serves(data.places[i], b) for b in bands) for i in must))
    rank = _rank(c)
    meals = sorted((p for p in cands if p.kind == "an" and p.id not in must), key=rank)
    others = sorted((p for p in cands if p.kind != "an" and p.id not in must), key=rank)
    base: Plan | None = None
    chosen: tuple[str, ...] = must
    for combo in combinations(meals, need):
        trial = must + tuple(p.id for p in combo)
        base = schedule(trial, c, data) if trial else None
        if base is not None:
            chosen = trial
            break
    if base is None and not (need == 0 and not must):
        return None
    return fill(base, c, others, data) if base is not None else fill(Plan(()), c, others, data)


def fill(plan: Plan, c: Constraints, cands: list[Place], data: Data) -> Plan | None:
    """Thêm dần ứng viên chưa có trong lịch (hợp sở thích trước) khi vẫn xếp được, tới MAX_STOPS.
    Điểm không khớp sở thích chỉ thêm khi lịch còn dưới 4 điểm hoặc khi nó lấp bớt ít nhất 30 phút trống,
    để không nhồi cho đủ số."""
    chosen, base = plan.ids, (plan if plan.stops else None)
    rank = _rank(c)
    rest = sorted((p for p in cands if p.id not in chosen and p.kind != "an"), key=rank)   # bữa ăn đã đủ
    for p in [o for o in rest if score(o, c) > 0] + [o for o in rest if score(o, c) <= 0]:
        if len(chosen) >= MAX_STOPS:
            break
        trial = schedule(chosen + (p.id,), c, data)
        if trial is None:
            continue
        if score(p, c) > 0 or len(chosen) < 4 or free_min(trial, c) <= free_min(base, c) - 30:
            chosen, base = chosen + (p.id,), trial
    return base


def free_min(plan: Plan | None, c: Constraints) -> int:
    """Số phút trong khung giờ không ở điểm nào (gồm cả thời gian đi lại)."""
    return (c.end - c.start) - (sum(s.leave - s.arrive for s in plan.stops) if plan else 0)


def stay_cap(p: Place) -> int:
    """Ở lâu nhất bao nhiêu phút khi kéo dài để lấp giờ trống: quán ăn thêm 30 phút,
    điểm khác gấp đôi thời gian tối thiểu hoặc thêm 60 phút, lấy mức lớn hơn."""
    return p.visit_min + 30 if p.kind == "an" else max(p.visit_min * 2, p.visit_min + 60)


def stretch(plan: Plan, c: Constraints, data: Data) -> Plan:
    """Lấp giờ chờ: kéo dài thời gian ở lại mỗi điểm tới khi phải đi điểm sau (hoặc hết khung giờ),
    trong giờ mở cửa và không quá stay_cap. Giờ đến không đổi nên verify vẫn rỗng."""
    stops = list(plan.stops)
    for i, s in enumerate(stops):
        p = data.places[s.place_id]
        until = (stops[i + 1].arrive - travel_min(s.place_id, stops[i + 1].place_id, data)
                 if i + 1 < len(stops) else c.end)
        closes = next((we for ws, we in p.open_windows if ws <= s.arrive and s.leave <= we), s.leave)
        stops[i] = Stop(s.place_id, s.arrive, max(s.leave, min(until, closes, s.arrive + stay_cap(p))))
    out = Plan(tuple(stops))
    return out if not verify(out, c, data) else plan


def idle_min(plan: Plan, i: int, data: Data) -> int:
    """Số phút rảnh trước điểm thứ i (sau khi trừ thời gian đi lại)."""
    a, b = plan.stops[i - 1], plan.stops[i]
    return b.arrive - a.leave - travel_min(a.place_id, b.place_id, data)


def diagnose(ids: tuple[str, ...], c: Constraints, data: Data) -> list[Violation]:
    """Vì sao một tập điểm không xếp được (để model chọn lại). Rỗng = không tìm ra lý do riêng nào."""
    v: list[Violation] = []
    unknown = [i for i in ids if i not in data.places]
    if unknown:
        return [Violation("UNKNOWN_PLACE", None, ", ".join(unknown))]
    if len(ids) > MAX_STOPS:
        v.append(Violation("TOO_MANY", None, "%d điểm, tối đa %d" % (len(ids), MAX_STOPS)))
    if len(set(ids)) != len(ids):
        v.append(Violation("DUPLICATE", None, "có id lặp"))
    places = [data.places[i] for i in ids]
    for p in places:
        if c.day is not None and c.day in p.closed_days:
            v.append(Violation("CLOSED", None, "%s nghỉ ngày này" % p.id))
        if p.id in c.exclude or set(p.tags) & set(c.avoid) or (p.kind == "an" and not set(c.diet) <= set(p.tags)):
            v.append(Violation("AVOID_TAG", None, "%s không hợp yêu cầu tránh hoặc ăn kiêng" % p.id))
    bands = required_meals(c)
    for p in places:
        if p.kind == "an" and bands and not any(serves(p, b) for b in bands):
            v.append(Violation("NO_MEAL", None, "%s chỉ mở %s, không làm bữa %s được; cần thêm quán khác cho bữa đó" % (
                p.id, ", ".join("%s-%s" % (fmt(a), fmt(b)) for a, b in p.open_windows),
                ", ".join("%s-%s" % (fmt(a), fmt(b)) for a, b in bands))))
    meals = sum(any(serves(p, b) for b in bands) for p in places)
    if meals < len(bands):
        v.append(Violation("NO_MEAL", None, "cần %d bữa, mới có %d quán ăn làm bữa được" % (len(bands), meals)))
    tickets = sum(ticket(p, c) for p in places)
    if tickets > c.budget_total:
        v.append(Violation("OVER_BUDGET", None, "riêng vé và ăn đã %d > %d" % (tickets, c.budget_total)))
    if not v:
        v.append(Violation("TRAVEL_GAP", None, "không có thứ tự nào kịp giờ mở cửa, đường đi và ngân sách; "
                                               "bỏ bớt điểm xa, điểm mở cửa hẹp hoặc điểm đắt"))
    return v


# ---------------------------------------------------------------- nới ràng buộc

BUDGET_STEPS = (50_000, 100_000, 200_000, 300_000, 500_000, 800_000, 1_200_000, 2_000_000, 3_000_000,
                5_000_000, 8_000_000)
WINDOW_STEPS = (60, 120, 180)


def _attempt(c: Constraints, data: Data) -> Plan | None:
    return plan_greedy(c, shortlist(c, data), data)


def fits_without_budget_limit(c: Constraints, data: Data) -> bool:
    """Bỏ giới hạn ngân sách thì xếp được không: phân biệt "thiếu tiền" với "không vừa giờ / bữa / đường đi"."""
    return _attempt(replace(c, budget_total=10 ** 12), data) is not None


def _min_budget(c: Constraints, data: Data) -> tuple[int, Plan] | None:
    lo, found = c.budget_total, None
    for extra in BUDGET_STEPS:
        b = c.budget_total + extra
        plan = _attempt(replace(c, budget_total=b), data)
        if plan is not None:
            found = (b, plan)
            break
        lo = b
    if found is None:
        return None
    hi, plan = found
    while hi - lo > 10_000:          # thu hẹp tới bậc 10.000đ
        mid = (lo + hi) // 2 // 10_000 * 10_000
        if mid <= lo:
            break
        p = _attempt(replace(c, budget_total=mid), data)
        if p is not None:
            hi, plan = mid, p
        else:
            lo = mid
    return hi, plan


def relax_options(c: Constraints, data: Data) -> list[Relax]:
    """1–3 cách nới, mỗi cách đã có lịch qua verify() với ràng buộc đã nới. Không bao giờ nới tag tránh hay món kiêng."""
    out: list[Relax] = []
    drops = (d for k in range(1, len(c.must) + 1) for d in combinations(c.must, k))   # bỏ ít điểm nhất trước
    for dropped in drops:
        c2 = replace(c, must=tuple(i for i in c.must if i not in dropped), exclude=c.exclude + dropped)
        plan = _attempt(c2, data)
        if plan is not None:
            out.append(Relax("drop", "drop=" + "+".join(dropped), c2, plan, dropped))
            break
    found = _min_budget(c, data)
    if found:
        b, plan = found
        out.append(Relax("budget", "budget_total=%d" % b, replace(c, budget_total=b), plan))
    for ext in WINDOW_STEPS:
        c2 = replace(c, end=min(24 * 60, c.end + ext))
        if c2.end == c.end:
            c2 = replace(c, start=max(5 * 60, c.start - ext))
        plan = _attempt(c2, data) if c2 != c else None
        if plan is not None:
            change = "end=%s" % fmt(c2.end) if c2.end != c.end else "start=%s" % fmt(c2.start)
            out.append(Relax("window", change, c2, plan))
            break
    for r in out:
        assert not verify(r.plan, r.constraints, data), r.change
    return out[:3]
