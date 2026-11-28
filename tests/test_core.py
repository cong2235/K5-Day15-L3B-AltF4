"""Test hành vi của lõi và luồng chính trên dữ liệu thử synthetic (tests/*_fixture.csv).

Chạy: python -m unittest discover -s tests
Kế hoạch viết tay dùng khoảng trống ≥ 30 phút giữa các điểm trong cùng thành phố, đủ cho travel_min ước tính.
"""
import json
import os
import re
import sys
import unittest
from dataclasses import replace

os.environ["ALTF4_DATA"] = "fixture"
os.environ["MODEL_PROVIDER"] = "fake"  # test lõi không gọi model thật, kể cả khi .env đã nối Bedrock
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import agent  # noqa: E402
import tools  # noqa: E402
import verify as core  # noqa: E402
from domain import Constraints, Plan, Stop, hhmm, request_from_dict  # noqa: E402
from rules import parse_rule  # noqa: E402

DATA = tools.data()
SAT, MON = 5, 0


def plan(*stops):
    return Plan(tuple(Stop(i, hhmm(a), hhmm(b)) for i, a, b in stops))


def c(**kw):
    base = dict(people=2, budget_total=1_000_000, day=SAT, start=hhmm("08:00"), end=hhmm("21:00"))
    base.update(kw)
    return Constraints(**base)


def codes(p, cons):
    return sorted(v.code for v in core.verify(p, cons, DATA))


class VerifyHandPlans(unittest.TestCase):
    """5 kế hoạch hợp lệ, 5 kế hoạch mỗi cái đúng một lỗi."""

    VALID = [
        (plan(("FX-01", "08:00", "09:30"), ("FX-05", "11:30", "12:15"), ("FX-06", "13:00", "13:45"),
              ("FX-07", "18:00", "19:00"), ("FX-04", "19:30", "20:30")), c()),
        (plan(("FX-06", "13:00", "13:45"), ("FX-02", "14:30", "15:30"), ("FX-05", "17:30", "18:15")),
         c(people=3, budget_total=600_000, day=2, start=hhmm("13:00"), end=hhmm("19:00"))),
        (plan(("FX-03", "09:00", "10:00"), ("FX-05", "11:00", "11:45")),
         c(people=1, budget_total=300_000, day=1, start=hhmm("09:00"), end=hhmm("12:00"))),
        (plan(("FX-07", "18:00", "19:00"), ("FX-04", "19:30", "20:30")),
         c(start=hhmm("17:30"), end=hhmm("21:00"))),
        (plan(("FX-01", "08:00", "09:30"), ("FX-05", "11:30", "12:15"), ("FX-06", "13:00", "13:45")),
         c(day=MON, start=hhmm("08:00"), end=hhmm("14:00"), avoid=("hai_san",), diet=("chay",))),
    ]

    def test_valid_plans_have_no_violation(self):
        for p, cons in self.VALID:
            with self.subTest(plan=p.ids):
                self.assertEqual(codes(p, cons), [])

    def test_closed_on_rest_day(self):
        p = plan(("FX-02", "09:00", "10:00"), ("FX-05", "11:30", "12:15"))
        self.assertEqual(codes(p, c(day=MON, end=hhmm("13:00"))), ["CLOSED"])

    def test_travel_gap(self):
        p = plan(("FX-01", "08:00", "09:30"), ("FX-03", "09:32", "10:32"), ("FX-05", "11:30", "12:15"))
        self.assertEqual(codes(p, c(end=hhmm("13:00"))), ["TRAVEL_GAP"])

    def test_over_budget(self):
        p = plan(("FX-01", "08:00", "09:30"), ("FX-04", "11:30", "12:30"))
        self.assertEqual(codes(p, c(budget_total=200_000, end=hhmm("13:00"))), ["OVER_BUDGET"])

    def test_no_lunch(self):
        p = plan(("FX-01", "09:00", "10:30"), ("FX-06", "11:00", "11:45"), ("FX-02", "12:30", "13:30"))
        self.assertEqual(codes(p, c(start=hhmm("09:00"), end=hhmm("14:00"))), ["NO_MEAL"])

    def test_avoid_tag(self):
        p = plan(("FX-01", "08:00", "09:30"), ("FX-05", "11:30", "12:15"))
        self.assertEqual(codes(p, c(end=hhmm("13:00"), avoid=("bien",))), ["AVOID_TAG"])

    def test_unknown_and_duplicate(self):
        p = plan(("FX-99", "08:00", "09:00"), ("FX-05", "11:30", "12:15"), ("FX-05", "12:30", "13:15"))
        self.assertEqual(codes(p, c(end=hhmm("14:00"))), ["DUPLICATE", "UNKNOWN_PLACE"])


class Planning(unittest.TestCase):
    def test_greedy_plan_is_valid_and_within_budget(self):
        cons = c(like=("bien", "hai_san"))
        p = core.plan_greedy(cons, core.shortlist(cons, DATA), DATA)
        self.assertIsNotNone(p)
        self.assertEqual(codes(p, cons), [])
        self.assertLessEqual(core.cost(p, cons, DATA).total, cons.budget_total)

    def test_must_far_place_over_budget_gives_verified_relax(self):
        cons = c(budget_total=600_000, must=("FX-08",), start=hhmm("07:00"))
        self.assertIsNone(core.plan_greedy(cons, core.shortlist(cons, DATA), DATA))
        options = core.relax_options(cons, DATA)
        self.assertTrue(options)
        kinds = {r.kind for r in options}
        self.assertIn("budget", kinds)
        self.assertIn("drop", kinds)
        for r in options:
            self.assertEqual(core.verify(r.plan, r.constraints, DATA), [])
            if r.kind == "budget":
                self.assertGreater(r.constraints.budget_total, cons.budget_total)

    def test_relax_never_loosens_diet_or_avoid(self):
        cons = c(budget_total=50_000, diet=("chay",), avoid=("hai_san",))
        for r in core.relax_options(cons, DATA):
            self.assertEqual((r.constraints.diet, r.constraints.avoid), (cons.diet, cons.avoid))


class RuleParsing(unittest.TestCase):
    """Câu tự viết cho test, không lấy từ eval/benchmark.csv."""

    def parse(self, text):
        return request_from_dict(parse_rule(text, list(DATA.places.values())), DATA.places)

    def test_full_request(self):
        r = self.parse("Ba đứa bọn mình, tổng 1,5 triệu, chủ nhật 9h sáng đến 8h tối, thích cafe, không thích biển")
        self.assertIsInstance(r, Constraints)
        self.assertEqual((r.people, r.budget_total, r.day, r.start, r.end), (3, 1_500_000, 6, 540, 1200))
        self.assertIn("cafe", r.like)
        self.assertIn("bien", r.avoid)
        self.assertNotIn("bien", r.like)

    def test_per_person_budget_is_multiplied(self):
        r = self.parse("5 người, mỗi người 200k, thứ 3 từ 10h đến 16h")
        self.assertEqual(r.budget_total, 1_000_000)

    def test_missing_fields_ask_exactly_one_question(self):
        for text, field in [("2 người, thứ Năm, 8h-18h, thích chợ", "budget"),
                            ("700k, thứ Năm, 8h-18h", "people"),
                            ("2 người 700k thứ Năm thích chợ", "window")]:
            with self.subTest(text=text):
                r = self.parse(text)
                self.assertEqual(getattr(r, "field", None), field)
                self.assertEqual(r.question.count("?"), 1)

    def test_out_of_scope(self):
        for text in ["Mua giúp mình vé tàu rồi thanh toán luôn", "Lịch 1 ngày ở Đà Lạt cho 2 người 1 triệu",
                     "Lịch 4 ngày 3 đêm ở Đà Nẵng nhé"]:
            with self.subTest(text=text):
                self.assertEqual(type(self.parse(text)).__name__, "OutOfScope")

    def test_named_place_becomes_must_and_unknown_is_kept(self):
        r = self.parse("2 người 900k thứ Bảy 8h-20h, muốn ghé Khu Núi Xa Thử và quán Bánh Xèo Bà Tư")
        self.assertIn("FX-08", r.must)
        self.assertEqual(r.unknown, ("Bánh Xèo Bà Tư",))


def block(output):
    m = re.search(r"```json\n(.*?)\n```\s*$", output, re.S)
    assert m, "output phải kết thúc bằng khối ```json"
    return json.loads(m.group(1))


class AnswerEndToEnd(unittest.TestCase):
    def test_plan_status_and_money_come_from_code(self):
        out = agent.answer("2 người, 1 triệu cả nhóm, thứ Bảy 8h đến 21h, thích biển và hải sản")["output"]
        j = block(out)
        self.assertEqual(j["status"], "plan")
        cons = c(like=("bien", "hai_san"))
        p = plan(*[(s["id"], s["arrive"], s["leave"]) for s in j["stops"]])
        self.assertEqual(codes(p, cons), [])
        self.assertEqual(j["total_vnd"], core.cost(p, cons, DATA).total)
        self.assertEqual(j["relax"], [])

    def test_rest_day_must_is_dropped_with_notice(self):
        out = agent.answer("2 người 600k thứ Hai 8h-17h, muốn đi Bảo tàng Thử rồi ăn trưa")["output"]
        j = block(out)
        self.assertEqual(j["status"], "plan")
        self.assertNotIn("FX-02", [s["id"] for s in j["stops"]])
        self.assertIn("đóng cửa", out)

    def test_infeasible_has_relax_and_no_stops(self):
        j = block(agent.answer("2 người 600k thứ Bảy 7h-21h, nhất định đi Khu Núi Xa Thử")["output"])
        self.assertEqual(j["status"], "infeasible")
        self.assertEqual(j["stops"], [])
        self.assertTrue(j["relax"])

    def test_ask_back_and_refuse_have_no_stops(self):
        for text, status in [("Đi thứ Bảy, 3 người, 8h-20h", "ask_back"),
                             ("Đặt giúp mình 3 vé cáp treo", "refuse")]:
            with self.subTest(text=text):
                out = agent.answer(text)["output"]
                j = block(out)
                self.assertEqual((j["status"], j["stops"]), (status, []))
        self.assertIn("lên lịch", agent.answer("Đặt giúp mình 3 vé cáp treo")["output"])


class FillGaps(unittest.TestCase):
    """Lịch không bỏ trống giờ khi còn cách lấp: kéo dài thời gian ở lại, khoảng còn lại ghi là thời gian rảnh."""

    def test_stretch_keeps_plan_valid_and_never_shrinks(self):
        cons = c(like=("bien", "hai_san"))
        p = core.plan_greedy(cons, core.shortlist(cons, DATA), DATA)
        s = core.stretch(p, cons, DATA)
        self.assertEqual(codes(s, cons), [])
        self.assertEqual([x.arrive for x in s.stops], [x.arrive for x in p.stops])
        for a, b in zip(p.stops, s.stops):
            self.assertGreaterEqual(b.leave, a.leave)
            self.assertLessEqual(b.leave - b.arrive, core.stay_cap(DATA.places[b.place_id]))
        self.assertLessEqual(sum(core.idle_min(s, i, DATA) for i in range(1, len(s.stops))),
                             sum(core.idle_min(p, i, DATA) for i in range(1, len(p.stops))))

    def test_remaining_gap_is_labelled_as_free_time(self):
        out = agent.answer("2 người, 1 triệu cả nhóm, thứ Bảy 8h đến 21h, thích biển và hải sản")["output"]
        j = block(out)
        p = plan(*[(s["id"], s["arrive"], s["leave"]) for s in j["stops"]])
        gaps = [core.idle_min(p, i, DATA) for i in range(1, len(p.stops))]
        self.assertEqual(out.count("rảnh khoảng"), sum(g >= agent.IDLE_NOTE_MIN for g in gaps))


class ChatTurns(unittest.TestCase):
    """Chat nhiều lượt (web): tin nhắn sau sửa trên yêu cầu và lịch trước. Ở đây đi nhánh luật (không có model)."""
    FIRST = "2 người, 1 triệu cả nhóm, thứ Bảy 8h đến 21h, thích biển và hải sản"

    def test_drop_a_stop_keeps_other_constraints(self):
        r1 = agent.answer(self.FIRST)
        first_id = block(r1["output"])["stops"][0]["id"]
        name = DATA.places[first_id].name
        r2 = agent.answer("bỏ %s đi" % name, r1["turn"])
        j = block(r2["output"])
        self.assertEqual(j["status"], "plan")
        self.assertNotIn(first_id, [s["id"] for s in j["stops"]])
        self.assertIn("bỏ: " + name, r2["output"])
        c2 = r2["turn"].constraints
        self.assertEqual((c2.people, c2.budget_total, c2.day), (2, 1_000_000, SAT))
        self.assertEqual(codes(r2["turn"].plan, c2), [])

    def test_change_budget_and_end_time(self):
        r1 = agent.answer(self.FIRST)
        r2 = agent.answer("tăng ngân sách lên 2 triệu, đi từ 9h đến 22h", r1["turn"])
        c2 = r2["turn"].constraints
        self.assertEqual((c2.budget_total, c2.start, c2.end, c2.like), (2_000_000, hhmm("09:00"), hhmm("22:00"),
                                                                       ("bien", "hai_san")))

    def test_answer_to_ask_back_is_merged(self):
        r1 = agent.answer("1 triệu, thứ Bảy 8h-21h, thích biển")
        self.assertEqual(block(r1["output"])["status"], "ask_back")
        r2 = agent.answer("2 người", r1["turn"])
        self.assertEqual(block(r2["output"])["status"], "plan")

    def test_refusal_keeps_the_plan_to_edit(self):
        r1 = agent.answer(self.FIRST)
        r2 = agent.answer("đặt giúp mình vé luôn nhé", r1["turn"])
        self.assertEqual(block(r2["output"])["status"], "refuse")
        self.assertIs(r2["turn"], r1["turn"])

    def test_excluded_place_is_a_violation(self):
        r1 = agent.answer(self.FIRST)
        p1 = r1["turn"].plan
        cons = replace(r1["turn"].constraints, exclude=(p1.stops[0].place_id,))
        self.assertIn("AVOID_TAG", codes(p1, cons))


class FakePrompts:
    """Đóng vai codebase/prompts.py của Công: propose chọn thiếu quán ăn, repair chọn lại đủ, why có chữ số."""

    def __init__(self):
        self.repairs = 0

    def parse_request(self, text):
        return {"status": "ok", "people": 2, "budget_total": 1_000_000, "day": "T7", "start": "08:00",
                "end": "13:00", "like": ["bien"], "avoid": [], "diet": [], "must_names": []}

    def propose(self, c, cands):
        return {"ids": ["FX-01"]}   # khung 08:00–13:00 cần bữa trưa → NO_MEAL

    def repair(self, c, cands, ids, problems):
        self.repairs += 1
        self.seen = sorted(v.code for v in problems)
        return {"ids": ["FX-01", "FX-05"]}

    def why(self, c, plan, places):
        return {"FX-01": "biển đẹp, vé 50k", "FX-05": "quán chay ngon"}


class AnswerWithPrompts(unittest.TestCase):
    def setUp(self):
        self.saved, agent.prompts = agent.prompts, FakePrompts()

    def tearDown(self):
        agent.prompts = self.saved

    def test_repair_loop_fixes_plan_and_reasons_cannot_carry_numbers(self):
        out = agent.answer("bất kỳ")["output"]
        j = block(out)
        self.assertEqual(j["status"], "plan")
        self.assertEqual(agent.prompts.repairs, 1)
        self.assertEqual(agent.prompts.seen, ["NO_MEAL"])
        self.assertNotIn("50k", out)
        self.assertIn("quán chay ngon", out)

    def test_model_times_are_ignored_code_schedules(self):
        # Giờ model ghi sai (chồng nhau, lệch bữa) không còn quan trọng: code tự xếp giờ cho tập điểm.
        agent.prompts.propose = lambda c, cands: {"stops": [{"id": "FX-01", "arrive": "08:00", "leave": "09:30"},
                                                            {"id": "FX-05", "arrive": "09:31", "leave": "10:16"}]}
        j = block(agent.answer("bất kỳ")["output"])
        self.assertEqual(j["status"], "plan")
        self.assertEqual(agent.prompts.repairs, 0)
        cons = c(end=hhmm("13:00"), like=("bien",))
        self.assertEqual(codes(plan(*[(s["id"], s["arrive"], s["leave"]) for s in j["stops"]]), cons), [])

    def test_invalid_json_from_model_falls_back_to_code(self):
        agent.prompts.propose = lambda c, cands: None
        j = block(agent.answer("bất kỳ")["output"])
        self.assertEqual(j["status"], "plan")
        cons = c(end=hhmm("13:00"), like=("bien",))
        self.assertEqual(codes(plan(*[(s["id"], s["arrive"], s["leave"]) for s in j["stops"]]), cons), [])


class MustPlaceCannotBeMainMeal(unittest.TestCase):
    """Lượt 2 (eval/report.md mục 3): điểm người dùng nêu mà không đi được như ý thì không được bỏ cả lịch."""

    BREAKFAST = replace(DATA.places["FX-05"], id="FX-11", name="Quán Bún Sáng Thử", open_windows=((hhmm("06:00"), hhmm("10:00")),))
    DATA2 = core.Data({**DATA.places, "FX-11": BREAKFAST}, DATA.overrides, DATA.rates)

    def test_breakfast_only_must_gets_a_plan_with_a_separate_lunch(self):
        cons = c(start=hhmm("09:00"), end=hhmm("17:00"), must=("FX-11", "FX-01"))
        p = core.plan_greedy(cons, core.shortlist(cons, self.DATA2), self.DATA2)
        self.assertIsNotNone(p)
        self.assertEqual(core.verify(p, cons, self.DATA2), [])
        self.assertIn("FX-11", p.ids)
        self.assertIn("FX-01", p.ids)
        self.assertTrue(any(core.serves(self.DATA2.places[s.place_id], core.LUNCH) and s.place_id != "FX-11"
                            for s in p.stops))
        self.assertIn("FX-11", core.diagnose(("FX-11", "FX-01"), cons, self.DATA2)[0].detail)

    def test_relax_drops_only_the_place_that_blocks_and_reason_names_its_ticket(self):
        cons = c(budget_total=1_000_000, must=("FX-01", "FX-08"))      # vé FX-08 2 × 900.000đ > 1.000.000đ
        drop = next(r for r in core.relax_options(cons, DATA) if r.kind == "drop")
        self.assertEqual(drop.dropped, ("FX-08",))
        self.assertIn("FX-01", drop.plan.ids)
        self.assertNotIn("FX-08", drop.plan.ids)
        why = " ".join(agent._why_infeasible(cons, DATA))
        self.assertIn("Khu Núi Xa Thử", why)
        self.assertIn("vượt ngân sách", why)


if __name__ == "__main__":
    unittest.main()
