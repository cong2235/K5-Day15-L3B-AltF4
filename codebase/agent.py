"""Luồng chính của bản chạy thử — Đức giữ file này. Hình dạng: workflow cố định (spec.md §4).

    parse_request → (từ chối | hỏi lại 1 câu) → shortlist → propose → verify → repair (≤ 3 vòng)
        → sạch: render lịch + lý do | vẫn vi phạm: relax_options → "không xếp được" + cách nới

Hợp đồng với khung: answer(text) -> {"output": str}. Cuối output luôn có khối ```json để grader đọc
(docs/design.md mục 8): {"status","stops","total_vnd","relax"}.
Chat nhiều lượt (web/server.py): answer(text, prev) với prev = khoá "turn" của lượt trước. Có lịch hay ràng buộc
từ trước thì tin nhắn mới được hiểu là sửa trên đó (revise_request); lượt trước là hỏi lại thì ghép câu trả lời vào câu cũ.

Hợp đồng với codebase/prompts.py (Công giữ). Mọi hàm đều tuỳ chọn; thiếu hàm, thiếu file, hoặc hàm trả None
(model trả JSON hỏng sau khi đã hỏi lại) thì luồng dùng phương án code và ghi note() vào trace.
Lỗi gọi model (mạng, key) cứ để bay ra cho khung ghi vào cột error.
    parse_request(text: str) -> dict | None          hình dạng: xem domain.request_from_dict
    revise_request(c, plan: Plan | None, text) -> dict | None   cùng hình dạng, đã áp tin nhắn sửa lên c
    propose(c: Constraints, cands: list[Place], previous: Plan | None) -> dict | None   {"ids":[...]}: model chọn điểm,
        code xếp thứ tự và giờ (verify.schedule). {"stops":[{"id",…}]} cũng nhận, giờ trong đó bị bỏ qua.
    repair(c, cands, ids: tuple[str, ...], problems: list[Violation]) -> dict | None   cùng hình dạng propose
    why(c: Constraints, plan: Plan, places: dict[str, Place]) -> dict | None   {place_id: lý do}
Lý do không được chứa chữ số (tiền, giờ do code viết), có chữ số thì bị thay bằng lý do do code dựng.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace

import rules
import tools
import verify as core
from domain import (DAY_NAMES, AskBack, Constraints, OutOfScope, Place, Plan, Relax, Stop, fmt, plan_from_dict,
                    plan_to_json, request_from_dict, vnd)
from tracing import note

try:
    import prompts  # codebase/prompts.py của Công
except ImportError:
    prompts = None

MAX_REPAIR = 3
IDLE_NOTE_MIN = 30   # khoảng trống từ chừng này phút trở lên thì ghi rõ là thời gian rảnh

TAG_LABEL = {"bien": "biển", "hai_san": "hải sản", "chay": "món chay", "an_vat": "ăn vặt", "cho": "chợ",
             "dac_san": "đặc sản", "cafe": "cafe", "check_in": "check-in", "van_hoa": "văn hoá",
             "tam_linh": "tâm linh", "thien_nhien": "thiên nhiên", "trong_nha": "trong nhà",
             "yen_tinh": "yên tĩnh", "soi_dong": "sôi động"}
CLUSTER_LABEL = {"my_khe": "Mỹ Khê – Ngũ Hành Sơn", "son_tra": "Sơn Trà", "trung_tam": "trung tâm",
                 "ba_na": "Bà Nà", "hoi_an": "Hội An"}
REFUSE_TEXT = {
    "booking": "Mình không đặt vé, đặt bàn hay thanh toán được. Bạn tự mua vé ở kênh chính thức của nơi đến nhé.",
    "other_place": "Hiện mình chỉ có dữ liệu Đà Nẵng (gồm Hội An), nên chưa lên lịch nơi khác được.",
    "multi_day": "Mình chỉ xếp lịch tham quan và ăn uống trong 1 ngày, không đặt phòng hay xếp lịch nhiều ngày.",
    "fake_review": "Mình không viết đánh giá hộ.",
    "prompt_leak": "Mình không chia sẻ hướng dẫn nội bộ.",
    "data_dump": "Mình không liệt kê toàn bộ dữ liệu và không bỏ qua ràng buộc của bạn.",
    "other": "Yêu cầu này nằm ngoài việc mình làm được.",
}
CAN_DO = ("Mình lên lịch 1 ngày ở Đà Nẵng được: cho mình biết ngân sách cả nhóm, số người, "
          "ngày đi và khung giờ, cùng sở thích nếu có.")


# ---------------------------------------------------------------- gọi AI (tuỳ chọn) hoặc phương án code

def _ai(name: str, *args):
    fn = getattr(prompts, name, None) if prompts is not None else None
    if fn is None:
        note("%s: chưa có prompts.%s, dùng phương án code" % (name, name))
        return None
    out = fn(*args)
    if out is None:
        note("%s: model trả JSON không hợp lệ, dùng phương án code" % name)
    return out


@dataclass(frozen=True)
class Turn:
    """Trạng thái giữ giữa các lượt chat. constraints None = lượt trước là hỏi lại (text là câu đã ghép)."""
    text: str
    constraints: Constraints | None = None
    plan: Plan | None = None
    options: tuple[Plan, ...] = ()   # các phương án đã đưa (web); người dùng chọn cái nào thì plan = cái đó


def _parse(text: str, places: dict[str, Place]):
    raw = _ai("parse_request", text)
    if raw is None:
        raw = rules.parse_rule(text, list(places.values()))
    return request_from_dict(raw, places)


def _revise(prev: Turn, text: str, places: dict[str, Place]):
    raw = _ai("revise_request", prev.constraints, prev.plan, text)
    if raw is None:
        raw = rules.revise_rule(prev.text, text, list(places.values()))
    return request_from_dict(raw, places)


def _unavailable(c: Constraints, places: dict[str, Place]) -> list[tuple[str, str]]:
    """Điểm bắt buộc mà hôm đó nghỉ, hoặc không mở đủ lâu trong khung giờ người dùng."""
    out = []
    for pid in c.must:
        p = places[pid]
        if c.day is not None and c.day in p.closed_days:
            out.append((pid, "%s đóng cửa (nghỉ) vào %s, nên mình không xếp." % (p.name, DAY_NAMES[c.day])))
        elif not any(min(we, c.end) - max(ws, c.start) >= p.visit_min for ws, we in p.open_windows):
            hours = ", ".join("%s–%s" % (fmt(a), fmt(b)) for a, b in p.open_windows)
            out.append((pid, "%s không mở đủ lâu trong khung giờ bạn chọn (giờ mở theo dữ liệu: %s), "
                             "nên mình không xếp." % (p.name, hours)))
    return out


def _snack_notes(c: Constraints, plan: Plan, data: core.Data) -> list[str]:
    """Quán người dùng muốn ăn nhưng không mở vào bữa chính: nói rõ là xếp lúc khác và bữa chính ở quán khác."""
    bands = core.required_meals(c)
    out = []
    for s in plan.stops:
        p = data.places[s.place_id]
        if p.id in c.must and p.kind == "an" and bands and not any(core.serves(p, b) for b in bands):
            hours = ", ".join("%s–%s" % (fmt(a), fmt(b)) for a, b in p.open_windows)
            out.append("%s chỉ mở %s theo dữ liệu, không kịp bữa chính, nên mình xếp ghé ăn lúc %s "
                       "và chọn quán khác cho bữa chính." % (p.name, hours, fmt(s.arrive)))
    return out


def _ids(raw) -> tuple[str, ...] | None:
    """Model chỉ chọn điểm: {"ids": [...]} (hoặc {"stops": [{"id"}]}, giờ trong đó bị bỏ qua)."""
    if not isinstance(raw, dict):
        return None
    items = raw.get("ids") if isinstance(raw.get("ids"), list) else [
        s.get("id") for s in raw.get("stops") or [] if isinstance(s, dict)]
    ids = tuple(dict.fromkeys(str(i) for i in items if i))
    return ids or None


def _plan(c: Constraints, cands: list[Place], data: core.Data, previous: Plan | None = None) -> Plan | None:
    """Model chọn tập điểm → code xếp thứ tự và giờ (schedule) → sai thì model chọn lại, tối đa MAX_REPAIR vòng.
    Có lịch thì code lấp thêm điểm (fill) và kéo dài thời gian ở lại (stretch) để bớt giờ trống.
    Model không đưa được tập xếp được thì dùng phương án code; vẫn không có thì None (không xếp được)."""
    ids = _ids(_ai("propose", c, cands, previous) if previous else _ai("propose", c, cands))
    plan = None
    for k in range(MAX_REPAIR + 1):
        if ids is None:
            break
        ids = tuple(dict.fromkeys(c.must + ids))
        plan = core.schedule(ids, c, data)
        if plan is not None:
            break
        problems = core.diagnose(ids, c, data)
        if k == MAX_REPAIR:
            note("model chưa chọn được tập điểm xếp được sau %d vòng: %s" % (MAX_REPAIR, problems[0].code))
            break
        ids = _ids(_ai("repair", c, cands, ids, problems))
    if plan is None:
        note("dùng phương án code để chọn điểm")
        plan = core.plan_greedy(c, cands, data)
        if plan is None:
            return None
    else:
        plan = core.fill(plan, c, cands, data) or plan
    return core.stretch(plan, c, data)


# ---------------------------------------------------------------- render (mọi số do code viết)

def _block(status: str, plan: Plan | None = None, total: int = 0, relax: list[Relax] = ()) -> str:
    body = {"status": status, "stops": plan_to_json(plan) if plan else [], "total_vnd": total,
            "relax": [{"change": r.change, "stops": plan_to_json(r.plan)} for r in relax]}
    return "```json\n%s\n```" % json.dumps(body, ensure_ascii=False)


def _understood(c: Constraints) -> str:
    parts = ["%d người" % c.people, "ngân sách %s cả nhóm (vé, ăn và đi lại)" % vnd(c.budget_total)]
    if c.day is not None:
        parts.append(DAY_NAMES[c.day])
    parts.append("%s–%s" % (fmt(c.start), fmt(c.end)))
    if c.like:
        parts.append("thích: " + ", ".join(TAG_LABEL[t] for t in c.like))
    if c.avoid:
        parts.append("tránh: " + ", ".join(TAG_LABEL[t] for t in c.avoid))
    if c.exclude:
        parts.append("bỏ: " + ", ".join(tools.data().places[i].name for i in c.exclude))
    if c.diet:
        parts.append("bữa ăn cần: " + ", ".join(TAG_LABEL[t] for t in c.diet))
    return "Mình hiểu: " + " · ".join(parts) + "."


def _reason(p: Place, stop, c: Constraints) -> str:
    bits = []
    if p.id in c.must:
        bits.append("bạn muốn ghé")
    if p.kind == "an":
        bits.append("bữa trưa" if stop.arrive < core.DINNER[0] else "bữa tối")
    liked = [TAG_LABEL[t] for t in p.tags if t in c.like]
    if liked:
        bits.append("hợp sở thích " + ", ".join(liked))
    if not bits:
        bits.append("lấp chỗ trống trong lịch, cụm " + CLUSTER_LABEL[p.cluster])
    return "; ".join(bits)


def _reasons(c: Constraints, plan: Plan, data: core.Data) -> dict[str, str]:
    raw = _ai("why", c, plan, data.places)
    out = {}
    for s in plan.stops:
        r = raw.get(s.place_id) if isinstance(raw, dict) else None
        if not isinstance(r, str) or not r.strip() or re.search(r"\d", r):
            r = _reason(data.places[s.place_id], s, c)
        out[s.place_id] = r.strip()
    return out


def _duration(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return " ".join(filter(None, ("%d tiếng" % h if h else "", "%d phút" % m if m else "")))


def _price(p: Place, c: Constraints) -> str:
    if p.price_pp == 0:
        return "miễn phí"
    if p.price_basis == "ca_nhom":
        return "%s cả nhóm" % vnd(p.price_pp)
    return "%s/người × %d = %s" % (vnd(p.price_pp), c.people, vnd(core.ticket(p, c)))


def _render_plan(c: Constraints, plan: Plan, notes: list[str], data: core.Data, why: dict | None = None) -> str:
    why = why if why is not None else _reasons(c, plan, data)
    cost = core.cost(plan, c, data)
    lines = [_understood(c), *notes, ""]
    for i, s in enumerate(plan.stops):
        p = data.places[s.place_id]
        if i:
            leg = "   ↳ đi lại ~%d phút (ước tính)" % core.travel_min(plan.stops[i - 1].place_id, p.id, data)
            if c.transport == "grab":
                leg += ", %s" % vnd(cost.legs[i - 1])
            idle = core.idle_min(plan, i, data)
            if idle >= IDLE_NOTE_MIN:
                leg += " · rảnh khoảng %s, nghỉ ngơi hoặc dạo quanh khu %s" % (
                    _duration(idle), CLUSTER_LABEL[data.places[plan.stops[i - 1].place_id].cluster])
            lines.append(leg)
        lines.append("%s–%s · %s — %s — %s" % (fmt(s.arrive), fmt(s.leave), p.name, _price(p, c), why[p.id]))
    lines.append("")
    if c.transport == "grab":
        lines.append("Tổng: %s, trong đó đi lại %s (ước tính). Ngân sách: %s." % (
            vnd(cost.total), vnd(sum(cost.legs)), vnd(c.budget_total)))
    else:
        lines.append("Tổng: %s, đã gồm thuê xe máy theo ngày (ước tính). Ngân sách: %s." % (
            vnd(cost.total), vnd(c.budget_total)))
    checked = min(data.places[s.place_id].checked_on for s in plan.stops)
    lines.append("Giờ mở cửa và giá là tham khảo theo dữ liệu kiểm ngày %s; hãy xác nhận lại với nơi đến trước khi đi."
                 % checked)
    lines.append(_block("plan", plan, cost.total))
    return "\n".join(lines)


def _relax_text(r: Relax, c: Constraints, data: core.Data) -> str:
    names = " → ".join(data.places[i].name for i in r.plan.ids)
    if r.kind == "budget":
        head = "Tăng ngân sách lên %s" % vnd(r.constraints.budget_total)
    elif r.kind == "window":
        mins = (c.start - r.constraints.start) + (r.constraints.end - c.end)
        head = "Đi thêm khoảng %d tiếng (%s)" % (round(mins / 60), "về muộn hơn" if r.constraints.end != c.end else "đi sớm hơn")
    else:
        head = "Bỏ " + ", ".join(data.places[i].name for i in r.dropped)
    return "%s: %s" % (head, names)


def _why_infeasible(c: Constraints, data: core.Data) -> list[str]:
    """Lý do lấy từ phép thử trên dữ liệu, không đoán theo loại cách nới."""
    must = [data.places[i] for i in c.must]
    paid = [p for p in must if core.ticket(p, c)]
    tickets = sum(core.ticket(p, c) for p in paid)
    why = []
    if tickets > c.budget_total:   # không ghi giá vé: điểm này không nằm trong lịch nào nên số đó không lần được về lịch
        why.append("riêng vé %s cho %d người đã vượt ngân sách %s" % (
            ", ".join(p.name for p in paid), c.people, vnd(c.budget_total)))
    if core.fits_without_budget_limit(c, data):
        if not why:
            why.append("tổng tiền vé, ăn và đi lại vượt ngân sách %s" % vnd(c.budget_total))
    else:
        why.append("kể cả không giới hạn tiền, %s không vừa khung giờ khi tính giờ mở cửa, bữa ăn và thời gian "
                   "di chuyển" % ("các điểm bạn chọn" if must else "không tổ hợp điểm nào"))
    return why


def _render_infeasible(c: Constraints, relax: list[Relax], notes: list[str], data: core.Data) -> str:
    must = ", ".join(data.places[i].name for i in c.must)
    why = _why_infeasible(c, data)
    lines = [_understood(c), *notes, "",
             "Mình không xếp được lịch nào thoả hết yêu cầu%s: %s." % (" với " + must if must else "", "; ".join(why))]
    if relax:
        lines.append("Các cách nới đã kiểm (mỗi cách đều có lịch hợp lệ):")
        lines += ["%d. %s" % (k, _relax_text(r, c, data)) for k, r in enumerate(relax, 1)]
        lines.append("Bạn chọn một cách thì mình xếp lịch chi tiết.")
    else:
        lines.append("Mình chưa tìm được cách nới nào trong dữ liệu hiện có.")
    lines.append(_block("infeasible", relax=relax))
    return "\n".join(lines)


# ---------------------------------------------------------------- luồng chính

def _understand(text: str, prev: Turn | None, data: core.Data):
    """Hiểu tin nhắn → ("done", kết quả trả ngay: từ chối / hỏi lại) hoặc ("ok", c, notes, full). Dùng chung cho
    answer() (khung eval) và answer_options() (web), để hai đường hiểu yêu cầu giống hệt nhau."""
    banner = ["[Đang dùng dữ liệu thử synthetic: %s, chưa có data/places.csv.]" % tools.source()] \
        if tools.using_fixture() else []
    if prev is not None and prev.constraints is not None:
        note("sửa trên yêu cầu trước")
        full = prev.text + "\n" + text
        req = _revise(prev, text, data.places)
    else:
        full = prev.text + "\n" + text if prev is not None else text   # trả lời cho câu hỏi lại
        req = _parse(full, data.places)
    if isinstance(req, OutOfScope):
        note("từ chối: %s" % req.reason)
        out = "\n".join(banner + [REFUSE_TEXT[req.reason], CAN_DO, _block("refuse")])
        return ("done", {"output": out, "turn": prev})       # giữ lịch cũ để người dùng sửa tiếp
    if isinstance(req, AskBack):
        note("hỏi lại: %s" % req.field)
        return ("done", {"output": "\n".join(banner + [req.question, _block("ask_back")]), "turn": Turn(full)})
    c = req
    notes = list(banner)
    notes += ["Mình chưa có dữ liệu về \"%s\", nên không xếp chỗ này và không đoán giờ hay giá." % n
              for n in c.unknown]
    for pid, msg in _unavailable(c, data.places):
        notes.append(msg)
        c = replace(c, must=tuple(x for x in c.must if x != pid))
    return ("ok", c, notes, full)


def answer(text: str, prev: Turn | None = None) -> dict:
    """{"output": str, "turn": Turn}. Khung eval gọi answer(text) và chỉ đọc "output"."""
    data = tools.data()
    step = _understand(text, prev, data)
    if step[0] == "done":
        return step[1]
    _, c, notes, full = step
    cands = tools.shortlist(c)
    plan = _plan(c, cands, data, prev.plan if prev is not None else None)
    if plan is not None and not core.verify(plan, c, data):
        notes += _snack_notes(c, plan, data)
        return {"output": _render_plan(c, plan, notes, data), "turn": Turn(full, c, plan)}
    note("không xếp được, tìm cách nới")
    return {"output": _render_infeasible(c, tools.relax_options(c), notes, data), "turn": Turn(full, c)}


# ---------------------------------------------------------------- nhiều phương án (chỉ web dùng, khung eval không gọi)

MAX_OPTIONS = 3
MIN_DIFF = 2          # phương án phụ phải khác phương án chính ít nhất chừng này điểm


def _valid(plan: Plan | None, c: Constraints, data: core.Data) -> bool:
    return plan is not None and not core.verify(plan, c, data) and set(c.must) <= set(plan.ids)


def _distinct(plan: Plan, chosen: list[Plan]) -> bool:
    return all(len(set(plan.ids) ^ set(p.ids)) >= MIN_DIFF for p in chosen)


def _from_ids(ids, c: Constraints, cands: list[Place], data: core.Data) -> Plan | None:
    """Tập điểm (AI chọn) → code xếp giờ, lấp thêm điểm, kéo dài thời gian ở. Không xếp được thì None."""
    ids = tuple(dict.fromkeys(c.must + tuple(i for i in ids if i in data.places)))
    plan = core.schedule(ids, c, data) if ids else None
    if plan is None:
        return None
    return core.stretch(core.fill(plan, c, cands, data) or plan, c, data)


def _code_variants(c: Constraints, main: Plan, data: core.Data):
    """Phương án dự phòng bằng code khi AI không đưa đủ: đổi gió (tránh điểm tham quan của lịch chính), tiết kiệm."""
    swap = tuple(i for i in main.ids if i not in c.must and data.places[i].kind != "an")
    c_swap = replace(c, exclude=tuple(dict.fromkeys(c.exclude + swap)))
    yield "Đổi gió, điểm khác", core.plan_greedy(c_swap, core.shortlist(c_swap, data), data)
    c_cheap = replace(c, like=())          # bỏ ưu tiên sở thích → xếp theo giá
    yield "Tiết kiệm hơn", core.plan_greedy(c_cheap, core.shortlist(c_cheap, data), data)


def _alternatives(c: Constraints, cands: list[Place], data: core.Data, main: Plan) -> list[tuple[str, Plan]]:
    out: list[tuple[str, Plan]] = []
    raw = _ai("propose_alternatives", c, cands, main, MAX_OPTIONS - 1)
    for opt in (raw or {}).get("options") or []:
        if len(out) >= MAX_OPTIONS - 1 or not isinstance(opt, dict) or not isinstance(opt.get("ids"), list):
            continue
        plan = _from_ids(tuple(str(i) for i in opt["ids"]), c, cands, data)
        label = str(opt.get("label") or "").strip()[:40] or "Phương án khác"
        if _valid(plan, c, data) and _distinct(plan, [main] + [p for _, p in out]):
            out.append((label, plan))
        else:
            note("phương án AI '%s' không xếp được hoặc trùng lịch chính, bỏ" % label)
    for label, plan in _code_variants(c, main, data):
        if len(out) >= MAX_OPTIONS - 1:
            break
        plan = core.stretch(plan, c, data) if plan is not None else None
        if _valid(plan, c, data) and _distinct(plan, [main] + [p for _, p in out]):
            note("thêm phương án bằng code: %s" % label)
            out.append((label, plan))
    return out


def _option_json(label: str, plan: Plan, c: Constraints, data: core.Data, why: dict[str, str]) -> dict:
    """Một phương án cho trang web: mọi giờ, tiền, toạ độ do code viết từ dữ liệu."""
    cost = core.cost(plan, c, data)
    stops = []
    for i, s in enumerate(plan.stops):
        p = data.places[s.place_id]
        leg = None
        if i:
            prev = plan.stops[i - 1].place_id
            leg = {"min": core.travel_min(prev, p.id, data), "idle": max(0, core.idle_min(plan, i, data)),
                   "vnd": cost.legs[i - 1] if c.transport == "grab" else 0}
        stops.append({"id": p.id, "name": p.name, "kind": p.kind, "lat": p.lat, "lon": p.lon,
                      "arrive": fmt(s.arrive), "leave": fmt(s.leave), "price": _price(p, c),
                      "why": why.get(p.id) or _reason(p, s, c), "leg": leg})
    return {"label": label, "total_vnd": cost.total, "transport_vnd": cost.transport,
            "budget_vnd": c.budget_total, "transport": c.transport, "stops": stops}


def _honor_new_likes(main: Plan, c: Constraints, prev: Turn | None, cands: list[Place], data: core.Data) -> Plan:
    """Người dùng vừa sửa "thay X bằng <loại hình>" mà lịch mới chưa có loại hình đó: thử đưa một ứng viên có tag đó
    vào (thay một điểm tham quan không bắt buộc, hoặc thêm nếu còn chỗ). Chỉ nhận lịch qua verify; không được thì giữ."""
    if prev is None or prev.constraints is None:
        return main
    added = set(c.like) - set(prev.constraints.like)
    if not added or any(set(data.places[i].tags) & added for i in main.ids):
        return main
    picks = [p for p in cands if set(p.tags) & added and p.kind != "an" and p.id not in main.ids][:3]
    drops = [None] + [i for i in reversed(main.ids) if i not in c.must and data.places[i].kind != "an"]
    for p in picks:
        for drop in drops:
            ids = tuple(i for i in main.ids if i != drop) + (p.id,)
            plan = core.schedule(ids, c, data) if len(ids) <= core.MAX_STOPS else None
            if _valid(plan, c, data):
                note("sửa theo yêu cầu: đưa %s vào lịch%s" % (p.id, " thay %s" % drop if drop else ""))
                return core.stretch(plan, c, data)
    return main


def answer_options(text: str, prev: Turn | None = None) -> dict:
    """Như answer(), thêm "options": 2–3 phương án đã qua verify (phương án đầu = lịch chính, giống answer()).
    Từ chối / hỏi lại / không xếp được thì "options" rỗng và dùng "output" như answer()."""
    data = tools.data()
    step = _understand(text, prev, data)
    if step[0] == "done":
        return {**step[1], "options": []}
    _, c, notes, full = step
    cands = tools.shortlist(c)
    main = _plan(c, cands, data, prev.plan if prev is not None else None)
    if not _valid(main, c, data):
        note("không xếp được, tìm cách nới")
        return {"output": _render_infeasible(c, tools.relax_options(c), notes, data), "turn": Turn(full, c),
                "options": []}
    main = _honor_new_likes(main, c, prev, cands, data)
    plans = [("Hợp yêu cầu nhất" if prev is None or prev.plan is None else "Lịch đã sửa", main)]
    plans += _alternatives(c, cands, data, main)
    seen: dict[str, Stop] = {}
    for _, p in plans:
        for s in p.stops:
            seen.setdefault(s.place_id, s)
    why = _reasons(c, Plan(tuple(seen.values())), data)      # một lần gọi model cho lý do của mọi phương án
    notes += _snack_notes(c, main, data)
    return {"output": _render_plan(c, main, notes, data, why), "turn": Turn(full, c, main, tuple(p for _, p in plans)),
            "options": [_option_json(label, p, c, data, why) for label, p in plans],
            "understood": _understood(c), "notes": notes,
            "checked_on": min(data.places[s.place_id].checked_on for _, p in plans for s in p.stops)}


def choose(turn: Turn | None, index: int) -> Turn | None:
    """Người dùng chọn phương án thứ index trên web → lịch đó thành nền cho các lần sửa sau."""
    if turn is None or not (0 <= index < len(turn.options)):
        return turn
    return replace(turn, plan=turn.options[index])
