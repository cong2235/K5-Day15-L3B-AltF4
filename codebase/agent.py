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
from domain import (DAY_NAMES, AskBack, Constraints, OutOfScope, Place, Plan, Relax, fmt, plan_from_dict,
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


def _render_plan(c: Constraints, plan: Plan, notes: list[str], data: core.Data) -> str:
    why = _reasons(c, plan, data)
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


def _render_infeasible(c: Constraints, relax: list[Relax], notes: list[str], data: core.Data) -> str:
    must = ", ".join(data.places[i].name for i in c.must)
    why = []
    if any(r.kind == "budget" for r in relax):
        why.append("tổng tiền vé, ăn và đi lại vượt ngân sách")
    if any(r.kind == "window" for r in relax) or any(r.kind == "drop" for r in relax):
        why.append("không đủ thời gian trong khung giờ, tính cả thời gian di chuyển")
    if not why:
        why.append("không có tổ hợp điểm nào thoả cùng lúc giờ mở cửa, thời gian di chuyển và ngân sách")
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

def answer(text: str, prev: Turn | None = None) -> dict:
    """{"output": str, "turn": Turn}. Khung eval gọi answer(text) và chỉ đọc "output"."""
    data = tools.data()
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
        return {"output": out, "turn": prev}       # giữ lịch cũ để người dùng sửa tiếp
    if isinstance(req, AskBack):
        note("hỏi lại: %s" % req.field)
        return {"output": "\n".join(banner + [req.question, _block("ask_back")]), "turn": Turn(full)}
    c = req
    notes = list(banner)
    notes += ["Mình chưa có dữ liệu về \"%s\", nên không xếp chỗ này và không đoán giờ hay giá." % n
              for n in c.unknown]
    for pid, msg in _unavailable(c, data.places):
        notes.append(msg)
        c = replace(c, must=tuple(x for x in c.must if x != pid))
    cands = tools.shortlist(c)
    plan = _plan(c, cands, data, prev.plan if prev is not None else None)
    if plan is not None and not core.verify(plan, c, data):
        return {"output": _render_plan(c, plan, notes, data), "turn": Turn(full, c, plan)}
    note("không xếp được, tìm cách nới")
    return {"output": _render_infeasible(c, tools.relax_options(c), notes, data), "turn": Turn(full, c)}
