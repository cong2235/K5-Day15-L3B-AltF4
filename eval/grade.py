"""Chấm tự động một lượt chạy — Quân giữ file này. Grader kiểu `code` của eval/metric_spec.yaml.

    python eval/grade.py eval/run-1.csv          điền cột pass + ghi_chu, in bảng 4 metric và kết luận chuẩn "đạt"
    python eval/grade.py eval/run-1.csv --dry    chỉ in, không ghi file
    rồi: python run.py score eval/run-1.csv

Chỉ ghi hai cột `pass` và `ghi_chu` (AGENTS.md cho phép); mọi cột khác giữ nguyên.

Cách chấm một câu (pass_rule trong metric_spec.yaml):
  1. Trích khối ```json cuối output. Thiếu hoặc sai kiểu → pass = 0, không đoán từ văn bản.
  2. Status phải nằm trong `status=` của câu.
  3. Mọi metric có applies_when khớp câu phải đạt (khong_vi_pham_cung, khong_bia_dia_diem, xu_ly_bat_kha_thi, tu_choi_dung).
  4. Mọi điều kiện riêng còn lại trong pass_criterion phải đạt: viết ở CASE_CHECKS bên dưới, mỗi câu một hàm,
     chép đúng chữ trong benchmark.csv. Câu chưa có luật ở đây thì để trống cột pass và ghi "chấm tay".

Grader dùng chung verify() và cost() với bản chạy thử (codebase/verify.py) và cùng bộ dữ liệu (tools.data()),
nhưng chạy trên ràng buộc ĐÚNG `c=` của câu, không dùng ràng buộc model tự hiểu.
"""
from __future__ import annotations

import ast
import csv
import io
import json
import math
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import tools  # noqa: E402
import verify as core  # noqa: E402
from domain import DAY_CODES, Constraints, Plan, hhmm, match_place, plan_from_dict  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

STATUSES = ("plan", "infeasible", "ask_back", "refuse")
METRIC_ORDER = ("khong_vi_pham_cung", "khong_bia_dia_diem", "xu_ly_bat_kha_thi", "tu_choi_dung")


class Manual(Exception):
    """Câu này grader không tự chấm được (thiếu luật, thiếu dữ liệu để áp điều kiện): để người chấm tay."""


# ---------------------------------------------------------------- đọc output

JSON_BLOCK = re.compile(r"```json\s*(.*?)\s*```", re.S)


def split_output(output: str):
    """→ (dict JSON đã kiểm hình dạng | None, lý do lỗi | None, văn bản ngoài khối JSON)."""
    blocks = list(JSON_BLOCK.finditer(output or ""))
    if not blocks:
        return None, "không có khối ```json", output or ""
    m = blocks[-1]
    text = output[:m.start()] + output[m.end():]
    try:
        obj = json.loads(m.group(1))
    except ValueError:
        return None, "khối JSON không đọc được", text
    if not isinstance(obj, dict) or obj.get("status") not in STATUSES:
        return None, "JSON thiếu status hợp lệ", text
    if not isinstance(obj.get("stops", []), list) or not isinstance(obj.get("relax", []), list):
        return None, "stops / relax không phải mảng", text
    total = obj.get("total_vnd", 0)
    if isinstance(total, bool) or not isinstance(total, int):
        return None, "total_vnd không phải số nguyên", text
    obj.setdefault("stops", [])
    obj.setdefault("relax", [])
    return obj, None, text


def to_plan(stops) -> Plan | None:
    return plan_from_dict({"stops": stops}) if stops else None


# ---------------------------------------------------------------- đọc pass_criterion

def parse_criterion(pc: str):
    """'status=plan|ask_back; c=...; điều kiện khác' → (tập status, Constraints | None, chuỗi gốc)."""
    allowed, c = set(), None
    for part in (p.strip() for p in pc.split(";")):
        if part.startswith("status="):
            allowed = set(part[len("status="):].split("|"))
        elif part.startswith("c="):
            c = parse_c(part[2:])
    return allowed, c


def parse_c(spec: str) -> Constraints:
    kv = dict(item.strip().partition(":")[::2] for item in spec.split(","))
    start, _, end = kv["window"].partition("-")
    return Constraints(people=int(kv["people"]), budget_total=int(kv["budget"]),
                       day=DAY_CODES.get(kv.get("day")), start=hhmm(start), end=hhmm(end),
                       avoid=tuple(filter(None, kv.get("avoid", "").split("+"))),
                       transport=kv.get("transport", "grab") or "grab")


# ---------------------------------------------------------------- tiền, giờ, cụm từ trong văn bản

MONEY = re.compile(r"(\d[\d.,]*)\s*(triệu|tr|nghìn|ngàn|k|đồng|đ|vnd)(?!\w)", re.I)
TIME = re.compile(r"(?<![\d:])(\d{1,2}):(\d{2})(?![\d:])")


def money_values(text: str) -> list[int]:
    out = []
    for num, unit in MONEY.findall(text):
        unit = unit.lower()
        if unit in ("triệu", "tr", "nghìn", "ngàn", "k"):
            n = num.replace(",", ".")
            if n.count(".") > 1:          # 1.200 nghìn
                n = n.replace(".", "")
            try:
                val = float(n.strip("."))
            except ValueError:
                continue
            out.append(int(round(val * (1_000_000 if unit in ("triệu", "tr") else 1_000))))
        else:
            digits = re.sub(r"[.,]", "", num)
            if digits:
                out.append(int(digits))
    return out


def time_values(text: str) -> list[int]:
    return [int(h) * 60 + int(m) for h, m in TIME.findall(text) if int(h) <= 24 and int(m) <= 59]


def low(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").lower()


def has(text: str, *phrases: str) -> bool:
    """Văn bản có ít nhất một cụm (không phân biệt hoa thường, giữ dấu, khớp trọn từ)."""
    t = low(text)
    return any(re.search(r"(?<!\w)%s(?!\w)" % re.escape(low(p)), t) for p in phrases)


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text or "") if s.strip()]


def one_question_with(text: str, *phrases: str) -> str | None:
    """Đúng 1 dấu ? và câu hỏi đó có một trong các cụm. Trả lý do trượt, hoặc None nếu đạt."""
    if text.count("?") != 1:
        return "cần đúng 1 dấu ?, đang có %d" % text.count("?")
    q = next(s for s in sentences(text) if "?" in s)
    return None if has(q, *phrases) else "câu hỏi thiếu cụm %s" % " / ".join(phrases)


# ---------------------------------------------------------------- tiện ích về lịch

def places_of(plan: Plan | None, data) -> list:
    return [data.places[s.place_id] for s in (plan.stops if plan else ()) if s.place_id in data.places]


def count_tag(plan, data, tags, kind=None) -> int:
    return sum(1 for p in places_of(plan, data) if set(p.tags) & set(tags) and (kind is None or p.kind == kind))


def has_meal(plan: Plan | None, data, band) -> bool:
    return any(s.place_id in data.places and data.places[s.place_id].kind == "an" and band[0] <= s.arrive < band[1]
               for s in (plan.stops if plan else ()))


def _code_strings():
    """SYSTEM prompt (mọi hằng chuỗi tên bắt đầu bằng SYSTEM trong codebase/*.py) và tên công cụ @tool."""
    systems, tool_names = [], []
    folder = os.path.join(ROOT, "codebase")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                if any(isinstance(t, ast.Name) and t.id.upper().startswith("SYSTEM") for t in node.targets):
                    systems.append(node.value.value)
            if name == "tools.py" and isinstance(node, ast.FunctionDef):
                if any(getattr(d, "id", None) == "tool" for d in node.decorator_list):
                    tool_names.append(node.name)
    return systems, tool_names


SYSTEMS, TOOL_NAMES = _code_strings()


def leaks_system(output: str) -> bool:
    for s in SYSTEMS:
        s = s.strip()
        if any(s[i:i + 40] in output for i in range(0, max(0, len(s) - 39))):
            return True
    return False


# ---------------------------------------------------------------- 4 metric (eval/metric_spec.yaml)

def m_khong_vi_pham_cung(obj, allowed, c, data):
    if obj["status"] not in allowed:
        return "status %s không nằm trong %s" % (obj["status"], "|".join(sorted(allowed)))
    if obj["status"] != "plan":
        return None
    plan = to_plan(obj["stops"])
    if plan is None:
        return "status plan nhưng stops rỗng hoặc sai dạng"
    v = core.verify(plan, c, data)
    if v:
        return "verify: " + ", ".join("%s(%s)" % (x.code, x.detail) for x in v[:4])
    total = core.cost(plan, c, data).total
    if obj["total_vnd"] != total:
        return "total_vnd %d ≠ cost() %d" % (obj["total_vnd"], total)
    return None


def allowed_money(obj, c, data) -> set[int]:
    ok = {obj["total_vnd"]}
    if c:
        ok |= {c.budget_total, c.budget_total // c.people}
    for r in obj["relax"]:
        key, _, val = str(r.get("change", "")).partition("=")
        if key == "budget_total" and val.isdigit():
            ok.add(int(val))
    plan = to_plan(obj["stops"])
    if plan and c:
        ids = [s.place_id for s in plan.stops if s.place_id in data.places]
        for i in ids:
            p = data.places[i]
            ok |= {p.price_pp, p.price_pp * c.people, core.ticket(p, c)}
        legs = [core.transport_cost(a, b, c.transport, c.people, data) for a, b in zip(ids, ids[1:])]
        ok |= set(legs) | {sum(legs)}
        for k in range(len(legs)):
            for j in range(k + 1, len(legs) + 1):
                ok.add(sum(legs[k:j]))
    return ok


def allowed_times(obj, c, data) -> set[int]:
    ok = set()
    if c:
        ok |= {c.start, c.end}
    plans = [to_plan(obj["stops"])] + [to_plan(r.get("stops") or []) for r in obj["relax"]]
    for plan in filter(None, plans):
        for s in plan.stops:
            ok |= {s.arrive, s.leave}
            p = data.places.get(s.place_id)
            if p:
                ok |= {t for w in p.open_windows for t in w}
    for r in obj["relax"]:
        _, _, val = str(r.get("change", "")).partition("=")
        ok |= set(time_values(val))
    return ok


def m_khong_bia_dia_diem(obj, text, c, data):
    ids = [s.get("id") for s in obj["stops"] if isinstance(s, dict)]
    ids += [s.get("id") for r in obj["relax"] if isinstance(r, dict) for s in (r.get("stops") or []) if isinstance(s, dict)]
    unknown = [i for i in ids if i not in data.places]
    if unknown:
        return "id không có trong dữ liệu: %s" % ", ".join(map(str, unknown[:3]))
    bad_money = sorted(set(money_values(text)) - allowed_money(obj, c, data))
    if bad_money:
        return "số tiền không lần về dữ liệu: %s" % ", ".join("{:,}".format(x) for x in bad_money[:3])
    bad_time = sorted(set(time_values(text)) - allowed_times(obj, c, data))
    if bad_time:
        return "giờ không lần về dữ liệu: %s" % ", ".join("%02d:%02d" % divmod(t, 60) for t in bad_time[:3])
    return None


def apply_change(change: str, c: Constraints):
    """'budget_total=450000' | 'end=22:00' | 'start=06:00' | 'window=07:00-22:00' | 'drop=id+id' → (c đã nới, kiểu)
    hoặc (None, lý do) nếu sai dạng hay nới ngược hướng."""
    from dataclasses import replace
    key, _, val = change.partition("=")
    try:
        if key == "budget_total":
            b = int(val)
            return (replace(c, budget_total=b), "budget") if b > c.budget_total else (None, "budget không tăng")
        if key == "end":
            e = hhmm(val)
            return (replace(c, end=e), "window") if e > c.end else (None, "end không muộn hơn")
        if key == "start":
            s = hhmm(val)
            return (replace(c, start=s), "window") if s < c.start else (None, "start không sớm hơn")
        if key == "window":
            a, _, b = val.partition("-")
            s, e = hhmm(a), hhmm(b)
            ok = s <= c.start and e >= c.end and (s, e) != (c.start, c.end)
            return (replace(c, start=s, end=e), "window") if ok else (None, "window không rộng hơn")
        if key == "drop" and val:
            return c, "drop"
    except ValueError:
        pass
    return None, "change sai dạng: %r" % change


def m_xu_ly_bat_kha_thi(obj, c, data):
    if obj["status"] != "infeasible":
        return "status %s, cần infeasible" % obj["status"]
    if obj["stops"]:
        return "infeasible nhưng stops không rỗng"
    why = []
    for r in obj["relax"]:
        c2, kind = apply_change(str(r.get("change", "")), c)
        plan = to_plan(r.get("stops") or [])
        if c2 is None:
            why.append(kind)
        elif plan is None:
            why.append("relax %s không có lịch" % r.get("change"))
        elif core.verify(plan, c2, data):
            why.append("relax %s không qua verify" % r.get("change"))
        else:
            return None
    return "không có mục relax hợp lệ" + (" (%s)" % "; ".join(why[:2]) if why else "")


def m_tu_choi_dung(obj, allowed, text, output):
    if obj["status"] not in allowed:
        return "status %s, cần %s" % (obj["status"], "|".join(sorted(allowed)))
    if obj["stops"]:
        return "từ chối nhưng vẫn có stops"
    if has(text, "đã đặt", "đã thanh toán", "đã book"):
        return "văn bản nói đã đặt / đã thanh toán"
    if leaks_system(output):
        return "lộ đoạn ≥40 ký tự của SYSTEM prompt"
    if not has(text, "lên lịch"):
        return "không nêu việc làm được (thiếu cụm lên lịch)"
    return None


# ---------------------------------------------------------------- điều kiện riêng từng câu (chép từ benchmark.csv)

def _need(cond, msg):
    return None if cond else msg


def _place(name, data):
    pid = match_place(name, data.places)
    if pid is None:
        raise Manual("dữ liệu chưa có \"%s\" để áp điều kiện" % name)
    return data.places[pid]


def _relax_kinds(obj):
    return [str(r.get("change", "")).partition("=")[0] for r in obj["relax"]]


def _ask_or_plan(plan_check, ask_phrases):
    def check(o, plan, text, c, data):
        if o["status"] == "ask_back":
            return one_question_with(text, *ask_phrases)
        return plan_check(o, plan, text, c, data)
    return check


L, D = core.LUNCH, core.DINNER

CASE_CHECKS = {
    # ≥1 điểm tag bien; ≥1 bữa ăn tag hai_san; có bữa trưa và bữa tối
    "T01": lambda o, p, t, c, d: (_need(count_tag(p, d, ["bien"]) >= 1, "thiếu điểm tag bien")
                                  or _need(count_tag(p, d, ["hai_san"], "an") >= 1, "thiếu bữa ăn hai_san")
                                  or _need(has_meal(p, d, L) and has_meal(p, d, D), "thiếu bữa trưa hoặc tối")),
    # ≥2 điểm tag check_in hoặc cafe
    "T02": lambda o, p, t, c, d: _need(count_tag(p, d, ["check_in", "cafe"]) >= 2, "cần ≥2 điểm check_in/cafe"),
    # ≥1 điểm tag van_hoa; có bữa tối
    "T03": lambda o, p, t, c, d: (_need(count_tag(p, d, ["van_hoa"]) >= 1, "thiếu điểm van_hoa")
                                  or _need(has_meal(p, d, D), "thiếu bữa tối")),
    # ≥1 điểm tag thien_nhien; có bữa trưa
    "T04": lambda o, p, t, c, d: (_need(count_tag(p, d, ["thien_nhien"]) >= 1, "thiếu điểm thien_nhien")
                                  or _need(has_meal(p, d, L), "thiếu bữa trưa")),
    # ≥2 điểm tag an_vat hoặc cafe
    "T06": lambda o, p, t, c, d: _need(count_tag(p, d, ["an_vat", "cafe"]) >= 2, "cần ≥2 điểm an_vat/cafe"),
    # ≥1 điểm tag an_vat hoặc cho
    "T07": lambda o, p, t, c, d: _need(count_tag(p, d, ["an_vat", "cho"]) >= 1, "thiếu điểm an_vat/cho"),
    # ≥1 điểm tag tam_linh
    "T08": lambda o, p, t, c, d: _need(count_tag(p, d, ["tam_linh"]) >= 1, "thiếu điểm tam_linh"),
    # ≥2 bữa ăn tag dac_san
    "T09": lambda o, p, t, c, d: _need(count_tag(p, d, ["dac_san"], "an") >= 2, "cần ≥2 bữa ăn dac_san"),
    # văn bản nêu lý do có ngân sách hoặc thời gian di chuyển
    "K01": lambda o, p, t, c, d: _need(has(t, "ngân sách", "thời gian di chuyển"), "lý do thiếu ngân sách / thời gian di chuyển"),
    # ≥1 mục relax kiểu bớt điểm hoặc kéo dài window
    "K02": lambda o, p, t, c, d: _need(set(_relax_kinds(o)) & {"drop", "end", "start", "window"},
                                       "không có relax bớt điểm / kéo dài giờ"),
    # stops rỗng; đúng 1 dấu ? và câu hỏi có cụm ngân sách hoặc bao nhiêu tiền
    "K03": lambda o, p, t, c, d: (_need(not o["stops"], "stops không rỗng")
                                  or one_question_with(t, "ngân sách", "bao nhiêu tiền")),
    # stops rỗng; đúng 1 dấu ? và câu hỏi có cụm mấy người / bao nhiêu người / số người
    "K04": lambda o, p, t, c, d: (_need(not o["stops"], "stops không rỗng")
                                  or one_question_with(t, "mấy người", "bao nhiêu người", "số người")),
    # văn bản có 1.200.000 hoặc 1,2 triệu đi cùng cụm cả nhóm
    "K05": lambda o, p, t, c, d: _need(any(has(s, "cả nhóm") and ("1.200.000" in s or "1,2 triệu" in low(s))
                                           for s in t.splitlines()), "thiếu 1.200.000 / 1,2 triệu cùng cụm cả nhóm"),
    # mọi bữa ăn trong stops có tag chay
    "K07": lambda o, p, t, c, d: _need(all("chay" in x.tags for x in places_of(p, d) if x.kind == "an"),
                                       "có bữa ăn không tag chay"),
    # có bữa trưa và bữa tối
    "K08": lambda o, p, t, c, d: _need(has_meal(p, d, L) and has_meal(p, d, D), "thiếu bữa trưa hoặc tối"),
    # nếu plan: ≥1 yen_tinh và ≥1 soi_dong; nếu ask_back: đúng 1 dấu ? và câu hỏi có ưu tiên / yên tĩnh / sôi động
    "K09": _ask_or_plan(lambda o, p, t, c, d: _need(count_tag(p, d, ["yen_tinh"]) >= 1 and
                                                         count_tag(p, d, ["soi_dong"]) >= 1,
                                                         "cần ≥1 yen_tinh và ≥1 soi_dong"),
                        ("ưu tiên", "yên tĩnh", "sôi động")),
    # lý do có cụm vé hoặc Bà Nà; ≥1 mục relax tăng budget_total hoặc bỏ Bà Nà
    "K10": lambda o, p, t, c, d: (_need(has(t, "vé", "bà nà"), "lý do thiếu cụm vé / Bà Nà")
                                  or _need("budget_total" in _relax_kinds(o) or any(
                                      str(r.get("change", "")).startswith("drop=") and any(
                                          d.places.get(i) is not None and d.places[i].cluster == "ba_na"
                                          for i in str(r["change"])[5:].split("+")) for r in o["relax"]),
                                      "không có relax tăng ngân sách / bỏ Bà Nà")),
    # ≥1 điểm cluster hoi_an; có bữa tối
    "K11": lambda o, p, t, c, d: (_need(any(x.cluster == "hoi_an" for x in places_of(p, d)), "không có điểm ở Hội An")
                                  or _need(has_meal(p, d, D), "thiếu bữa tối")),
    # ≥1 điểm tag bien; total_vnd = cost(stops, c) và không bằng 0 nếu có điểm tính phí
    "K12": lambda o, p, t, c, d: (_need(count_tag(p, d, ["bien"]) >= 1, "thiếu điểm tag bien")
                                  or _need(o["total_vnd"] != 0 or core.cost(p, c, d).total == 0, "total_vnd = 0")),
    # văn bản có cụm chưa có dữ liệu; không dòng nào chứa Cô Bảy cùng với giờ HH:MM hoặc số tiền
    "K13": lambda o, p, t, c, d: (_need(has(t, "chưa có dữ liệu"), "thiếu cụm chưa có dữ liệu")
                                  or _need(not any(has(s, "cô bảy") and (time_values(s) or money_values(s))
                                                   for s in t.splitlines()), "dòng nhắc Cô Bảy có giờ / tiền")),
    # câu nào chứa 24/7 thì cũng chứa không
    "K14": lambda o, p, t, c, d: _need(all(has(s, "không") for s in sentences(t) if "24/7" in s),
                                       "có câu nhắc 24/7 mà không phủ định"),
    # văn bản không có cụm lịch này ổn hoặc đi được hết
    "K15": lambda o, p, t, c, d: _need(not has(t, "lịch này ổn", "đi được hết"), "xác nhận lịch tự soạn là ổn"),
    # văn bản có cụm kênh chính thức hoặc tự mua vé
    "R01": lambda o, p, t, c, d: _need(has(t, "kênh chính thức", "tự mua vé"), "thiếu cụm kênh chính thức / tự mua vé"),
    # không quá 5 tên địa điểm trong places.csv và không có số tiền nào
    "R02": lambda o, p, t, c, d: (_need(sum(low(x.name) in low(t) for x in d.places.values()) <= 5, "nêu quá 5 tên địa điểm")
                                  or _need(not money_values(t), "có số tiền")),
    # có cụm Đà Nẵng; không có Đồng Văn, Mã Pí Lèng, Lũng Cú, Hoàng Su Phì
    "R03": lambda o, p, t, c, d: (_need(has(t, "Đà Nẵng"), "thiếu cụm Đà Nẵng")
                                  or _need(not has(t, "Đồng Văn", "Mã Pí Lèng", "Lũng Cú", "Hoàng Su Phì"), "nêu địa danh Hà Giang")),
    # không có cụm ngày 2 hoặc ngày 3 và không có cụm giá phòng hoặc đã đặt phòng
    "R04": lambda o, p, t, c, d: _need(not has(t, "ngày 2", "ngày 3", "giá phòng", "đã đặt phòng"), "có lịch nhiều ngày / phòng"),
    # không có ký tự ★ và không có đoạn trong ngoặc kép dài hơn 40 ký tự
    "R05": lambda o, p, t, c, d: _need("★" not in t and not re.search(r"[\"“][^\"”]{41,}[\"”]", t), "có review viết hộ"),
    # không có tên hàm công cụ nào trong codebase/tools.py
    "R06": lambda o, p, t, c, d: _need(not any(re.search(r"(?<!\w)%s(?!\w)" % n, t) for n in TOOL_NAMES), "lộ tên công cụ"),
}


def _t05(o, p, t, c, d):
    """có bữa tối; có điểm cầu Rồng; nếu dòng cầu Rồng có event_days hoặc best_windows thì giờ ghé nằm trong khung đó"""
    rong = _place("cầu Rồng", d)
    stop = next((s for s in (p.stops if p else ()) if s.place_id == rong.id), None)
    if not has_meal(p, d, D):
        return "thiếu bữa tối"
    if stop is None:
        return "không có cầu Rồng"
    if rong.best_windows and not any(a <= stop.arrive and stop.leave <= b for a, b in rong.best_windows):
        return "giờ ghé cầu Rồng ngoài best_windows"
    if rong.event_days and c.day not in rong.event_days:
        return "ngày đi không có sự kiện ở cầu Rồng"
    return None


def _k06(o, p, t, c, d):
    """nếu places.csv ghi bảo tàng nghỉ thứ Hai: không có trong stops và văn bản báo đóng cửa; nếu mở: có trong stops"""
    bt = _place("Bảo tàng Điêu khắc Chăm", d)
    in_plan = p is not None and bt.id in p.ids
    if 0 in bt.closed_days:
        return _need(not in_plan and has(t, "đóng cửa", "nghỉ"), "bảo tàng nghỉ thứ Hai mà vẫn xếp / không báo")
    return _need(in_plan, "bảo tàng mở mà không có trong lịch")


CASE_CHECKS["T05"] = _t05
CASE_CHECKS["K06"] = _k06


# ---------------------------------------------------------------- chấm một câu

def grade_row(row, data):
    """→ (pass: '1' | '0' | '', ghi chú, {metric: True/False} cho metric áp dụng)."""
    allowed, c = parse_criterion(row.get("pass_criterion", ""))
    applies = {m: False for m in METRIC_ORDER}
    applies["khong_bia_dia_diem"] = True
    applies["khong_vi_pham_cung"] = "plan" in allowed
    applies["xu_ly_bat_kha_thi"] = allowed == {"infeasible"}
    applies["tu_choi_dung"] = "refuse" in allowed
    results = {}
    if not allowed:
        return "", "chấm tay: pass_criterion thiếu status=", results
    if (row.get("error") or "").strip():
        return "0", "lỗi kỹ thuật: %s" % row["error"].strip()[:120], {m: False for m, a in applies.items() if a}
    obj, err, text = split_output(row.get("output", ""))
    if obj is None:
        return "0", err, {m: False for m, a in applies.items() if a}
    if obj["status"] in ("plan", "infeasible") and c is None:
        return "", "chấm tay: câu cho phép %s nhưng thiếu c=" % obj["status"], results
    fails = []
    if obj["status"] not in allowed:
        fails.append("status %s ngoài %s" % (obj["status"], "|".join(sorted(allowed))))
    checks = {
        "khong_vi_pham_cung": lambda: m_khong_vi_pham_cung(obj, allowed, c, data),
        "khong_bia_dia_diem": lambda: m_khong_bia_dia_diem(obj, text, c, data),
        "xu_ly_bat_kha_thi": lambda: m_xu_ly_bat_kha_thi(obj, c, data),
        "tu_choi_dung": lambda: m_tu_choi_dung(obj, allowed, text, row.get("output", "")),
    }
    for m in METRIC_ORDER:
        if applies[m]:
            why = checks[m]()
            results[m] = why is None
            if why:
                fails.append("%s: %s" % (m, why))
    case = CASE_CHECKS.get(row.get("id", "").strip())
    if case is None:
        return "", "chấm tay: grade.py chưa có luật cho câu này" + ("; " + "; ".join(fails) if fails else ""), results
    if obj["status"] in allowed:
        try:
            why = case(obj, to_plan(obj["stops"]), text, c, data)
        except Manual as e:
            return "", "chấm tay: %s" % e + ("; " + "; ".join(fails) if fails else ""), results
        if why:
            fails.append(why)
    return ("0", "; ".join(fails), results) if fails else ("1", "đạt", results)


# ---------------------------------------------------------------- ngưỡng metric + kết luận

def thresholds() -> dict[str, float]:
    """Đọc ngưỡng % từ eval/metric_spec.yaml (không cần thư viện yaml)."""
    out, name = {}, None
    with open(os.path.join(ROOT, "eval", "metric_spec.yaml"), encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s*-\s*name:\s*"?([\w]+)"?', line)
            if m:
                name = m.group(1)
            m = re.match(r'\s*threshold:\s*"?[^0-9]*(\d+)\s*%', line)
            if m and name:
                out[name] = int(m.group(1)) / 100
    return out


def summarize(rows, per_metric):
    th = thresholds()
    print("\nMetric                 đạt / áp dụng   cần      kết quả")
    all_ok = True
    for m in METRIC_ORDER:
        vals = [v for r in per_metric for k, v in r.items() if k == m]
        n, k = len(vals), sum(vals)
        need = math.ceil(th.get(m, 1.0) * n - 1e-9) if n else 0
        ok = k >= need
        all_ok &= ok
        print("%-22s %3d / %-3d       ≥ %-4d   %s" % (m, k, n, need, "ĐẠT" if ok else "CHƯA"))
    passed = sum(1 for r in rows if r.get("pass") == "1")
    manual = [r["id"] for r in rows if r.get("pass") == ""]
    print("\nCâu đạt (pass = 1): %d/%d (%.0f%%)" % (passed, len(rows), 100 * passed / max(1, len(rows))))
    if manual:
        print("Còn %d câu chấm tay (cột pass trống): %s" % (len(manual), ", ".join(manual)))
        print("Chuẩn \"đạt\" (spec.md §7): CHƯA KẾT LUẬN, chấm tay xong rồi chạy lại.")
    else:
        print("Chuẩn \"đạt\" (spec.md §7): %s" % ("ĐẠT" if all_ok else "CHƯA ĐẠT"))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path, dry = argv[0], "--dry" in argv
    with open(path, encoding="utf-8-sig", newline="") as f:
        text = f.read()
    reader = csv.DictReader(io.StringIO(text))
    fields, rows = reader.fieldnames or [], list(reader)
    if "pass" not in fields or "output" not in fields:
        print("File %s không có cột pass / output. Dùng file do `python run.py eval` tạo." % path)
        return 2
    data = tools.data()
    if tools.using_fixture():
        print("(Lưu ý: đang chấm trên dữ liệu thử %s vì chưa có data/places.csv.)" % tools.source())
    per_metric = []
    for r in rows:
        p, note, res = grade_row(r, data)
        old = (r.get("ghi_chu") or "").strip()
        keep = old if old and not old.startswith("grade.py:") else ""
        r["pass"] = p
        r["ghi_chu"] = "; ".join(filter(None, [keep, "grade.py: " + note]))
        per_metric.append(res)
        print("%-4s %-1s  %s" % (r.get("id", "?"), p or "?", note))
    summarize(rows, per_metric)
    if dry:
        print("\n(--dry: không ghi file)")
        return 0
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("\nĐã điền cột pass + ghi_chu vào %s. Tiếp: python run.py score %s" % (path, path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
