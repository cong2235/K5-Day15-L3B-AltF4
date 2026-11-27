"""Phương án quay về bằng luật (docs/discovery.md 3.2, mức "Rule"). Đức giữ file này.

Dùng khi chưa có codebase/prompts.py hoặc model trả JSON hỏng. Trả ĐÚNG hình dạng JSON mà
prompts.parse_request trả (xem domain.request_from_dict), nên cả hai đi qua một biên kiểm duy nhất.
Luật viết theo cách người Việt hay gõ, không so khớp nguyên văn câu thử nào.
"""
from __future__ import annotations

import re

from domain import CLUSTERS, Place, norm

# ---------------------------------------------------------------- từ chối (lớp 3)

OTHER_PLACES = ("ha giang", "ha noi", "sai gon", "ho chi minh", "sapa", "sa pa", "da lat", "nha trang",
                "phu quoc", "hue", "ha long", "quy nhon", "vung tau", "ninh binh", "can tho", "phu yen")
REFUSE_PATTERNS = (
    ("booking", r"\bdat\b(?:\s+\w+){0,3}\s+(ve|ban|tour)\b|\bthanh toan\b|\bbook\b|\bmua ve giup\b"),
    ("multi_day", r"\b[2-9] ngay\b|\b\d+ dem\b|\bkhach san\b|\bdat phong\b|\bhomestay\b"),
    ("fake_review", r"\breview\b|\bdanh gia \d sao\b|\b\d sao\b"),
    ("prompt_leak", r"system prompt|\bprompt\b|cong cu noi bo|huong dan he thong"),
    ("data_dump", r"liet ke (toan bo|tat ca|het)|toan bo dia diem|tat ca dia diem"),
)
OVERRIDE = r"bo qua (het )?(moi |tat ca )?(quy tac|gioi han|rang buoc|huong dan)"

# ---------------------------------------------------------------- sở thích → tag
# Mỗi tag: (từ có dấu, so trên chữ thường gốc) và (từ không dấu, so trên bản không dấu). Tách hai loại vì
# "chợ" và "chỗ" cùng thành "cho" khi bỏ dấu.
TAG_WORDS = {
    "bien": (("biển", "tắm biển"), ("bien", "beach")),
    "hai_san": (("hải sản",), ("hai san", "seafood")),
    "cafe": (("cà phê", "cafe", "cafè"), ("ca phe", "cafe", "coffee")),
    "check_in": (("check-in", "check in", "sống ảo", "view đẹp", "chụp ảnh"), ("check in", "check-in", "song ao")),
    "van_hoa": (("văn hoá", "văn hóa", "lịch sử", "bảo tàng", "phố cổ"), ("van hoa", "lich su", "bao tang", "pho co", "museum")),
    "tam_linh": (("chùa", "tâm linh"), ("tam linh", "temple", "pagoda")),
    "thien_nhien": (("thiên nhiên", "leo núi", "núi"), ("thien nhien", "leo nui", "nature", "hiking")),
    "an_vat": (("ăn vặt",), ("an vat", "street food", "snack")),
    "cho": (("chợ",), ("cho dem", "market")),
    "dac_san": (("đặc sản", "mì quảng", "bánh tráng"), ("dac san", "mi quang", "banh trang", "local food")),
    "yen_tinh": (("yên tĩnh", "không đông", "chill"), ("yen tinh", "chill", "quiet")),
    "soi_dong": (("sôi động", "chợ đêm", "náo nhiệt"), ("soi dong", "cho dem", "nightlife")),
}
NEGATORS = r"(không thích|ko thích|k thích|không muốn|tránh|dị ứng|không ăn được|không ăn|khong thich|ko thich|k thich|khong muon|tranh|di ung|khong an)"
CLUSTER_WORDS = {"hoi an": "hoi_an", "ba na": "ba_na", "son tra": "son_tra", "my khe": "my_khe"}

# ---------------------------------------------------------------- số, giờ, ngày

NUM_WORDS = {"mot": 1, "hai": 2, "ba": 3, "bon": 4, "nam": 5, "sau": 6, "bay": 7, "tam": 8}
PEOPLE_UNITS = r"(nguoi|dua|ban|sinh vien|friends?|people|persons?|thanh vien)"
DAYS = (
    (0, r"thu (hai|2)\b|\bt2\b|monday"), (1, r"thu (ba|3)\b|\bt3\b|tuesday"), (2, r"thu (tu|4)\b|\bt4\b|wednesday"),
    (3, r"thu (nam|5)\b|\bt5\b|thursday"), (4, r"thu (sau|6)\b|\bt6\b|friday"),
    (5, r"thu (bay|7)\b|\bt7\b|saturday"), (6, r"chu nhat|\bcn\b|sunday"),
)
DAY_CODE = ("T2", "T3", "T4", "T5", "T6", "T7", "CN")
FULL_DAY = r"ca ngay|full day|whole day|all day"
_T = r"(\d{1,2})(?:\s*(?:h|g|gio|:)\s*(\d{2})?|\s*(am|pm))\s*(sang|trua|chieu|toi|dem|am|pm)?"
TIME = re.compile(_T)
TIME_RANGE = re.compile(_T + r"\s*(?:-|–|—|~|den|toi|to|until)\s*" + _T)


def _people(t: str) -> int | None:
    if re.search(r"vo chong|cap doi|hai dua|2 dua|couple", t):
        return 2
    if re.search(r"mot minh|di mot minh|\balone\b|\bsolo\b", t):
        return 1
    m = re.search(r"\b(\d{1,2}|%s)\s*%s\b" % ("|".join(NUM_WORDS), PEOPLE_UNITS), t)
    if not m:
        m = re.search(r"\b(?:nhom|we are|chung minh|tui minh)\s*(\d{1,2})\b", t)
    if not m:
        return None
    raw = m.group(1)
    return int(raw) if raw.isdigit() else NUM_WORDS[raw]


def _amount(num: str, unit: str) -> int | None:
    unit = unit.lower()
    if unit in ("tr", "trieu", "triệu", "cu", "củ"):
        return int(round(float(num.replace(",", ".")) * 1_000_000)) if re.fullmatch(r"\d+([.,]\d{1,2})?", num) else None
    digits = int(re.sub(r"[.,]", "", num))
    if unit in ("k", "nghin", "nghìn", "ngan", "ngàn"):
        return digits * 1000
    return digits                                   # đ, d, vnd, dong: đã là đồng


def _budget(text: str, people: int | None) -> int | None:
    low = text.lower()
    m = re.search(r"(\d+(?:[.,]\d+)*)\s*(k|nghìn|nghin|ngàn|ngan|triệu|trieu|tr|củ|cu|vnd|đồng|dong|đ|d)\b", low)
    if not m:
        return None
    amount = _amount(m.group(1), m.group(2))
    if amount is None or amount < 1000:
        return None
    window = norm(low[max(0, m.start() - 40): m.end() + 25])
    per_person = re.search(r"moi (nguoi|ban|dua)|/ ?nguoi|mot nguoi|per person|each", window)
    if per_person:
        return amount * people if people else None
    return amount


def _hour(g: tuple) -> int:
    h, mi, ampm, part = int(g[0]), int(g[1] or 0), g[2], g[3]
    mark = ampm or part
    if mark in ("pm", "chieu", "toi", "dem") and h < 12:
        h += 12
    if mark == "am" and h == 12:
        h = 0
    return min(24 * 60, h * 60 + mi)


def _pair(g1: tuple, g2: tuple) -> tuple[str, str] | None:
    if int(g1[0]) > 24 or int(g2[0]) > 24:
        return None
    a, b = _hour(g1), _hour(g2)
    if b <= a and b + 12 * 60 <= 24 * 60 and not (g2[2] or g2[3]):
        b += 12 * 60                                 # "từ 8h đến 6h" hiểu là 6h chiều
    return ("%02d:%02d" % divmod(a, 60), "%02d:%02d" % divmod(b, 60)) if b > a else None


def _window(t: str) -> tuple[str, str] | None:
    for m in TIME_RANGE.finditer(t):                 # ưu tiên khoảng viết rõ: "8h–17h", "từ 8h đến 21h"
        pair = _pair(m.groups()[:4], m.groups()[4:])
        if pair:
            return pair
    hits = [m.groups() for m in TIME.finditer(t)]
    if len(hits) >= 2:
        pair = _pair(hits[0], hits[1])
        if pair:
            return pair
    if re.search(FULL_DAY, t):
        return "08:00", "21:00"
    return None


def _tags(text: str, t: str) -> tuple[list[str], list[str]]:
    low = text.lower()
    like, avoid = [], []
    for tag, (marked, plain) in TAG_WORDS.items():
        words = [(w, low) for w in marked] + [(w, t) for w in plain]
        hit = False
        for w, src in words:
            for m in re.finditer(r"(?<!\w)%s(?!\w)" % re.escape(w), src):
                hit = True
                before = src[max(0, m.start() - 22): m.start()]
                if re.search(NEGATORS + r"[^,.;]*$", before):
                    avoid.append(tag)
        if hit and tag not in avoid:
            like.append(tag)
    return list(dict.fromkeys(like)), list(dict.fromkeys(avoid))


def _mentions(text: str, t: str, places: list[Place]) -> tuple[list[str], list[str]]:
    """Tên điểm có trong data mà người dùng nhắc, và tên riêng ("quán Cô Ba…") mà data không có."""
    found: list[Place] = []
    for p in places:
        keys = [norm(k) for k in (p.name, *p.aliases)]
        if any(k and re.search(r"\b%s\b" % re.escape(k), t) for k in keys):
            found.append(p)
    for word, cluster in CLUSTER_WORDS.items():
        if re.search(r"\b%s\b" % word, t) and not any(p.cluster == cluster for p in found):
            in_cluster = sorted((p for p in places if p.cluster == cluster and p.kind == "tham_quan"),
                                key=lambda p: (-p.visit_min, p.id))
            if in_cluster:
                found.append(in_cluster[0])
    unknown = []
    for m in re.finditer(r"\b(?:quán|tiệm|nhà hàng)\s+([^,.;!?\n]+)", text, flags=re.IGNORECASE):
        name = m.group(1).strip()
        if not re.search(r"[A-ZÀ-Ỹ]", name):        # không có chữ hoa → không phải tên riêng ("quán hải sản")
            continue
        if not any(norm(k) and norm(k) in norm(name) for p in places for k in (p.name, *p.aliases)):
            unknown.append(re.split(r"\s+(?:ở|tại|gần)\s+", name)[0].strip())
    return [p.name for p in dict.fromkeys(found)], unknown


def parse_rule(text: str, places: list[Place]) -> dict:
    t = norm(text)
    people = _people(t)
    budget = _budget(text, people)
    window = _window(t)
    for reason, pattern in REFUSE_PATTERNS:
        if re.search(pattern, t):
            return {"status": "refuse", "reason": reason}
    if any(re.search(r"\b%s\b" % p, t) for p in OTHER_PLACES):
        return {"status": "refuse", "reason": "other_place"}
    if re.search(OVERRIDE, t) and (budget is None or people is None or window is None):
        return {"status": "refuse", "reason": "data_dump"}   # đòi bỏ quy tắc mà không có yêu cầu hợp lệ
    day = next((DAY_CODE[d] for d, pat in DAYS if re.search(pat, t)), None)
    like, avoid = _tags(text, t)
    diet = ["chay"] if re.search(r"\ban chay\b|\bchay\b|vegetarian|vegan", t) else []
    like = [x for x in like if x != "chay"]
    must, unknown = _mentions(text, t, places)
    base = next((c for w, c in CLUSTER_WORDS.items() if re.search(r"\b(o gan|gan|o)\s+(bien\s+)?%s\b" % w, t)), None)
    return {
        "status": "ok", "people": people, "budget_total": budget, "day": day,
        "start": window[0] if window else None, "end": window[1] if window else None,
        "like": like, "avoid": avoid, "diet": diet,
        "transport": "xe_may" if re.search(r"xe may|motorbike|scooter", t) else "grab",
        "must_names": must + unknown, "base_cluster": base if base in CLUSTERS else None,
    }
