"""Mô hình miền và biên kiểm (docs/design.md mục 5). Đức giữ file này.

Mọi dữ liệu từ ngoài (CSV, JSON model trả, kết quả luật) đi qua các hàm *_from_* ở đây.
Sau biên này, lõi (verify.py) tin kiểu, không kiểm lại.
Giờ luôn là số phút từ 00:00 (int), không dùng chuỗi trong lõi.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["tham_quan", "an", "cafe"]
KINDS = ("tham_quan", "an", "cafe")
CLUSTERS = ("my_khe", "son_tra", "trung_tam", "ba_na", "hoi_an")
FAR_CLUSTERS = ("ba_na", "hoi_an")
TAGS = ("bien", "hai_san", "chay", "an_vat", "cho", "dac_san", "cafe", "check_in", "van_hoa",
        "tam_linh", "thien_nhien", "trong_nha", "yen_tinh", "soi_dong")
TRANSPORTS = ("grab", "xe_may")
DAY_CODES = {"T2": 0, "T3": 1, "T4": 2, "T5": 3, "T6": 4, "T7": 5, "CN": 6}
DAY_NAMES = ("thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ Nhật")
VIOLATION_CODES = ("UNKNOWN_PLACE", "CLOSED", "OVERLAP", "TRAVEL_GAP", "OVER_BUDGET",
                   "OUT_OF_WINDOW", "NO_MEAL", "AVOID_TAG", "TOO_MANY", "DUPLICATE")
REFUSE_REASONS = ("booking", "other_place", "multi_day", "fake_review", "prompt_leak", "data_dump", "other")


class DataError(ValueError):
    """Dữ liệu trong data/ sai định dạng. Thông báo có tên file và số dòng."""


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    kind: Kind
    cluster: str
    tags: tuple[str, ...]
    open_windows: tuple[tuple[int, int], ...]
    closed_days: tuple[int, ...]
    visit_min: int
    price_pp: int
    price_basis: Literal["moi_nguoi", "ca_nhom"]
    lat: float
    lon: float
    source: str
    checked_on: str
    aliases: tuple[str, ...] = ()
    best_windows: tuple[tuple[int, int], ...] = ()
    event_days: tuple[int, ...] = ()


@dataclass(frozen=True)
class Constraints:
    people: int
    budget_total: int            # VND cả nhóm: vé + ăn + đi lại (không gồm chỗ ở)
    day: int | None              # 0 = thứ Hai … 6 = Chủ Nhật; None = chưa biết
    start: int                   # phút
    end: int
    like: tuple[str, ...] = ()
    avoid: tuple[str, ...] = ()
    base_cluster: str | None = None
    transport: str = "grab"
    must: tuple[str, ...] = ()   # id điểm người dùng nêu tên, phải có trong lịch
    diet: tuple[str, ...] = ()   # tag mọi bữa ăn phải có, ví dụ ("chay",)
    unknown: tuple[str, ...] = ()  # tên người dùng nêu mà data không có
    exclude: tuple[str, ...] = ()  # id điểm người dùng đã bỏ khi sửa lịch, không được xếp lại


@dataclass(frozen=True)
class Stop:
    place_id: str
    arrive: int
    leave: int


@dataclass(frozen=True)
class Plan:
    stops: tuple[Stop, ...]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(s.place_id for s in self.stops)


@dataclass(frozen=True)
class Violation:
    code: str
    stop_index: int | None
    detail: str


@dataclass(frozen=True)
class AskBack:
    field: Literal["budget", "people", "window"]
    question: str


@dataclass(frozen=True)
class OutOfScope:
    reason: str                  # một giá trị trong REFUSE_REASONS


@dataclass(frozen=True)
class Relax:
    kind: Literal["budget", "window", "drop"]
    change: str                  # dạng tên=giá trị, ví dụ budget_total=450000
    constraints: Constraints
    plan: Plan
    dropped: tuple[str, ...] = field(default=())


# ---------------------------------------------------------------- giờ, chữ

def hhmm(text: str) -> int:
    """'07:30' → 450. Nhận '24:00' = 1440."""
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", text)
    if not m:
        raise ValueError("giờ phải dạng HH:MM, đang là %r" % text)
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 24 or mi > 59 or (h == 24 and mi):
        raise ValueError("giờ ngoài 00:00–24:00: %r" % text)
    return h * 60 + mi


def fmt(minutes: int) -> str:
    return "%02d:%02d" % divmod(minutes, 60)


def vnd(amount: int) -> str:
    return "{:,}".format(amount).replace(",", ".") + "đ"


def norm(text: str) -> str:
    """Bỏ dấu, chữ thường, gộp khoảng trắng: 'Bà Nà Hills' → 'ba na hills'."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text.lower()).strip()


def _windows(text: str) -> tuple[tuple[int, int], ...]:
    out = []
    for part in filter(None, (p.strip() for p in text.split(";"))):
        a, sep, b = part.partition("-")
        if not sep:
            raise ValueError("khung giờ phải dạng HH:MM-HH:MM, đang là %r" % part)
        s, e = hhmm(a), hhmm(b)
        if e <= s:
            raise ValueError("khung giờ kết thúc trước khi bắt đầu: %r" % part)
        out.append((s, e))
    return tuple(sorted(out))


def _ints(text: str, lo: int, hi: int) -> tuple[int, ...]:
    vals = tuple(int(x) for x in filter(None, (p.strip() for p in text.split(";"))))
    if any(v < lo or v > hi for v in vals):
        raise ValueError("giá trị ngoài %d–%d: %r" % (lo, hi, text))
    return vals


def _list(text: str) -> tuple[str, ...]:
    return tuple(filter(None, (p.strip() for p in (text or "").split(";"))))


# ---------------------------------------------------------------- đọc CSV (biên)

PLACE_COLUMNS = ("id", "name", "kind", "cluster", "tags", "open_windows", "closed_days", "visit_min",
                 "price_pp", "price_basis", "lat", "lon", "source", "checked_on")


def _rows(path: str, required: tuple[str, ...]):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise DataError("%s thiếu cột: %s" % (path, ", ".join(missing)))
        for n, row in enumerate(reader, start=2):
            yield n, {k: (v or "").strip() for k, v in row.items() if k}


def load_places(path: str) -> dict[str, Place]:
    places: dict[str, Place] = {}
    for n, r in _rows(path, PLACE_COLUMNS):
        try:
            if r["kind"] not in KINDS:
                raise ValueError("kind phải là một trong %s" % (KINDS,))
            if r["cluster"] not in CLUSTERS:
                raise ValueError("cluster phải là một trong %s" % (CLUSTERS,))
            if r["price_basis"] not in ("moi_nguoi", "ca_nhom"):
                raise ValueError("price_basis phải là moi_nguoi hoặc ca_nhom")
            tags = _list(r["tags"])
            bad = [t for t in tags if t not in TAGS]
            if bad:
                raise ValueError("tag lạ %s (thêm vào data/DATA_CARD.md và domain.TAGS trước)" % bad)
            p = Place(
                id=r["id"], name=r["name"], kind=r["kind"], cluster=r["cluster"], tags=tags,
                open_windows=_windows(r["open_windows"]), closed_days=_ints(r["closed_days"], 0, 6),
                visit_min=int(r["visit_min"]), price_pp=int(r["price_pp"]), price_basis=r["price_basis"],
                lat=float(r["lat"]), lon=float(r["lon"]), source=r["source"], checked_on=r["checked_on"],
                aliases=_list(r.get("aliases", "")), best_windows=_windows(r.get("best_windows", "")),
                event_days=_ints(r.get("event_days", ""), 0, 6))
            if not p.id or p.id in places:
                raise ValueError("id trống hoặc bị lặp: %r" % p.id)
            if not p.open_windows or p.visit_min <= 0 or p.price_pp < 0:
                raise ValueError("cần open_windows, visit_min > 0, price_pp ≥ 0")
        except (ValueError, KeyError) as e:
            raise DataError("%s dòng %d: %s" % (path, n, e)) from None
        places[p.id] = p
    if not places:
        raise DataError("%s không có dòng nào" % path)
    return places


def load_overrides(path: str, places: dict[str, Place]) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    for n, r in _rows(path, ("from_id", "to_id", "minutes")):
        a, b = r["from_id"], r["to_id"]
        if a not in places or b not in places:
            raise DataError("%s dòng %d: id không có trong places: %s → %s" % (path, n, a, b))
        out[(a, b)] = out[(b, a)] = int(r["minutes"])
    return out


@dataclass(frozen=True)
class Rate:
    mode: str
    base_vnd: int
    per_km_vnd: int
    per_day_vnd: int


def load_rates(path: str) -> dict[str, Rate]:
    out: dict[str, Rate] = {}
    for n, r in _rows(path, ("mode", "base_vnd", "per_km_vnd", "per_day_vnd")):
        if r["mode"] not in TRANSPORTS:
            raise DataError("%s dòng %d: mode phải là một trong %s" % (path, n, TRANSPORTS))
        try:
            out[r["mode"]] = Rate(r["mode"], int(r["base_vnd"] or 0), int(r["per_km_vnd"] or 0),
                                  int(r["per_day_vnd"] or 0))
        except ValueError as e:
            raise DataError("%s dòng %d: %s" % (path, n, e)) from None
    return out


# ---------------------------------------------------------------- JSON từ model / luật (biên)
#
# Hình dạng chung mà prompts.parse_request (Công) và rules.parse_rule cùng trả:
#   {"status": "ok" | "ask_back" | "refuse",
#    "reason": một giá trị REFUSE_REASONS (khi refuse),
#    "people": int | null, "budget_total": int | null (VND cả nhóm, đã nhân số người nếu cần),
#    "day": "T2".."T7" | "CN" | null, "start": "HH:MM" | null, "end": "HH:MM" | null,
#    "like": [tag], "avoid": [tag], "diet": [tag], "transport": "grab" | "xe_may",
#    "must_names": [tên điểm người dùng nêu], "base_cluster": cluster | null,
#    "exclude_names": [tên điểm người dùng bỏ khi sửa lịch]  (tuỳ chọn)}

QUESTIONS = {
    "budget": "Nhóm mình định chi tổng cộng bao nhiêu tiền cho cả ngày, tính cả vé, ăn và đi lại?",
    "people": "Nhóm mình đi mấy người?",
    "window": "Nhóm mình muốn đi từ mấy giờ đến mấy giờ?",
}


def _tags(value) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(dict.fromkeys(t for t in value if isinstance(t, str) and t in TAGS))


def _pos_int(value) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and value > 0:
        return int(value)
    if isinstance(value, str) and value.strip().isdigit() and int(value) > 0:
        return int(value)
    return None


def match_place(name: str, places: dict[str, Place]) -> str | None:
    """Tên người dùng nêu → id, so không dấu với name và aliases. Không khớp thì None."""
    key = norm(name)
    if not key:
        return None
    for p in places.values():
        for cand in (p.name, *p.aliases):
            c = norm(cand)
            if c and (c == key or re.search(r"\b%s\b" % re.escape(c), key) or re.search(r"\b%s\b" % re.escape(key), c)):
                return p.id
    return None


def request_from_dict(d, places: dict[str, Place]) -> Constraints | AskBack | OutOfScope:
    """Kiểm JSON yêu cầu ở biên. Thiếu ngân sách, số người hoặc khung giờ thì hỏi lại đúng 1 câu.
    Không bao giờ điền mặc định cho tiền hay số người."""
    if not isinstance(d, dict):
        return OutOfScope("other")
    status = d.get("status")
    if status == "refuse":
        reason = d.get("reason")
        return OutOfScope(reason if reason in REFUSE_REASONS else "other")
    budget = _pos_int(d.get("budget_total"))
    if budget is None:
        return AskBack("budget", QUESTIONS["budget"])
    people = _pos_int(d.get("people"))
    if people is None or people > 20:
        return AskBack("people", QUESTIONS["people"])
    try:
        start, end = hhmm(d["start"]), hhmm(d["end"])
    except (KeyError, TypeError, ValueError):
        return AskBack("window", QUESTIONS["window"])
    if end <= start:
        return AskBack("window", QUESTIONS["window"])
    day = DAY_CODES.get(d.get("day")) if isinstance(d.get("day"), str) else None
    must, unknown = [], []
    for name in d.get("must_names") or []:
        if not isinstance(name, str):
            continue
        pid = match_place(name, places)
        if pid and pid not in must:
            must.append(pid)
        elif not pid:
            unknown.append(name.strip())
    exclude = []
    for name in d.get("exclude_names") or []:
        pid = match_place(name, places) if isinstance(name, str) else None
        if pid and pid not in exclude:
            exclude.append(pid)
    must = [m for m in must if m not in exclude]
    transport = d.get("transport") if d.get("transport") in TRANSPORTS else "grab"
    base = d.get("base_cluster") if d.get("base_cluster") in CLUSTERS else None
    avoid = _tags(d.get("avoid"))
    like = tuple(t for t in _tags(d.get("like")) if t not in avoid)
    return Constraints(people=people, budget_total=budget, day=day, start=start, end=end, like=like,
                       avoid=avoid, base_cluster=base, transport=transport, must=tuple(must),
                       diet=_tags(d.get("diet")), unknown=tuple(unknown), exclude=tuple(exclude))


def plan_from_dict(d) -> Plan | None:
    """{"stops":[{"id","arrive","leave"}]} → Plan. Sai hình dạng thì None. id lạ vẫn giữ để verify báo UNKNOWN_PLACE."""
    if not isinstance(d, dict) or not isinstance(d.get("stops"), list) or not d["stops"]:
        return None
    stops = []
    for s in d["stops"]:
        try:
            stops.append(Stop(str(s["id"]), hhmm(s["arrive"]), hhmm(s["leave"])))
        except (KeyError, TypeError, ValueError):
            return None
    return Plan(tuple(stops))


def plan_to_json(plan: Plan) -> list[dict]:
    return [{"id": s.place_id, "arrive": fmt(s.arrive), "leave": fmt(s.leave)} for s in plan.stops]
