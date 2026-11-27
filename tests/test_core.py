"""Test hành vi của lõi và luồng chính trên dữ liệu thử synthetic (tests/*_fixture.csv).

Chạy: python -m unittest discover -s tests
Kế hoạch viết tay dùng khoảng trống ≥ 30 phút giữa các điểm trong cùng thành phố, đủ cho travel_min ước tính.
"""
import json
import os
import re
import sys
import unittest

os.environ["ALTF4_DATA"] = "fixture"
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


class FakePrompts:
    """Đóng vai codebase/prompts.py của Công: propose trả lịch lệch giờ, repair sửa đúng, why có chữ số."""

    def __init__(self):
        self.repairs = 0

    def parse_request(self, text):
        return {"status": "ok", "people": 2, "budget_total": 1_000_000, "day": "T7", "start": "08:00",
                "end": "13:00", "like": ["bien"], "avoid": [], "diet": [], "must_names": []}

    def propose(self, c, cands):
        return {"stops": [{"id": "FX-01", "arrive": "08:00", "leave": "09:30"},
                          {"id": "FX-05", "arrive": "09:31", "leave": "10:16"}]}   # TRAVEL_GAP + NO_MEAL

    def repair(self, c, cands, plan, violations):
        self.repairs += 1
        self.seen = sorted(v.code for v in violations)
        return {"stops": [{"id": "FX-01", "arrive": "08:00", "leave": "09:30"},
                          {"id": "FX-05", "arrive": "11:30", "leave": "12:15"}]}

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
        self.assertEqual(agent.prompts.seen, ["NO_MEAL", "TRAVEL_GAP"])
        self.assertNotIn("50k", out)
        self.assertIn("quán chay ngon", out)

    def test_invalid_json_from_model_falls_back_to_code(self):
        agent.prompts.propose = lambda c, cands: None
        j = block(agent.answer("bất kỳ")["output"])
        self.assertEqual(j["status"], "plan")
        cons = c(end=hhmm("13:00"), like=("bien",))
        self.assertEqual(codes(plan(*[(s["id"], s["arrive"], s["leave"]) for s in j["stops"]]), cons), [])


if __name__ == "__main__":
    unittest.main()
