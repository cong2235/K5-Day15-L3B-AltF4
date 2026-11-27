"""Kiểm grade.py bằng output viết tay trên bộ dữ liệu thử (tests/*_fixture.csv). Quân giữ file này.

    python eval/test_grade.py

Mỗi test là một output tự viết: một bản đúng phải đạt, mỗi bản sai một lỗi phải bị bắt đúng metric.
"""
import json
import os
import sys
import unittest

os.environ["ALTF4_DATA"] = "fixture"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grade  # noqa: E402
from domain import Plan, Stop, hhmm  # noqa: E402

DATA = grade.tools.data()
C_T01 = "status=plan; c=people:2,budget:800000,day:T7,window:08:00-21:00; ≥1 điểm tag bien; ≥1 bữa ăn tag hai_san; có bữa trưa và bữa tối"
STOPS = [("FX-01", "08:00", "09:30"), ("FX-04", "11:00", "12:00"), ("FX-06", "14:00", "14:45"), ("FX-05", "17:00", "17:45")]


def block(status, stops=(), total=0, relax=()):
    body = {"status": status, "stops": [{"id": i, "arrive": a, "leave": b} for i, a, b in stops],
            "total_vnd": total, "relax": list(relax)}
    return "```json\n%s\n```" % json.dumps(body, ensure_ascii=False)


def total_of(stops, crit=C_T01):
    _, c = grade.parse_criterion(crit)
    plan = Plan(tuple(Stop(i, hhmm(a), hhmm(b)) for i, a, b in stops))
    return grade.core.cost(plan, c, DATA).total, grade.core.verify(plan, c, DATA)


def row(case_id, crit, output):
    return {"id": case_id, "pass_criterion": crit, "output": output, "error": ""}


class GradeTest(unittest.TestCase):
    def setUp(self):
        self.total, violations = total_of(STOPS)
        self.assertEqual(violations, [], "lịch mẫu viết tay phải hợp lệ trên fixture")
        self.text = ("Mình hiểu: 2 người, ngân sách 800.000đ cả nhóm, 08:00–21:00.\n"
                     "08:00–09:30 Bãi biển Thử\n11:00–12:00 Quán Hải Sản Thử — 150.000đ/người\n"
                     "14:00–14:45 Cafe Thử\n17:00–17:45 Quán Chay Thử\n")

    def grade(self, case_id, crit, output):
        p, note, _ = grade.grade_row(row(case_id, crit, output), DATA)
        return p, note

    def test_lich_dung_thi_dat(self):
        self.assertEqual(self.grade("T01", C_T01, self.text + block("plan", STOPS, self.total)), ("1", "đạt"))

    def test_thieu_khoi_json(self):
        p, note = self.grade("T01", C_T01, self.text)
        self.assertEqual(p, "0")
        self.assertIn("không có khối", note)

    def test_sua_total_vnd(self):
        p, note = self.grade("T01", C_T01, self.text + block("plan", STOPS, self.total - 1000))
        self.assertEqual(p, "0")
        self.assertIn("total_vnd", note)

    def test_dia_diem_bia(self):
        bad = STOPS[:3] + [("DN-999", "17:00", "17:45")]
        p, note = self.grade("T01", C_T01, self.text + block("plan", bad, self.total))
        self.assertEqual(p, "0")
        self.assertIn("UNKNOWN_PLACE", note)

    def test_gia_bia_trong_van_ban(self):
        p, note = self.grade("T01", C_T01, self.text + "Vé vào cửa 999.000đ.\n" + block("plan", STOPS, self.total))
        self.assertEqual(p, "0")
        self.assertIn("số tiền không lần về dữ liệu", note)

    def test_gio_bia_trong_van_ban(self):
        p, note = self.grade("T01", C_T01, self.text + "Quán mở tới 03:15 sáng.\n" + block("plan", STOPS, self.total))
        self.assertEqual(p, "0")
        self.assertIn("giờ không lần về dữ liệu", note)

    def test_den_luc_dong_cua(self):
        late = STOPS[:3] + [("FX-04", "15:00", "16:00")]   # quán hải sản nghỉ 14:00–17:00 và bị lặp
        total, _ = total_of(late)
        p, note = self.grade("T01", C_T01, self.text + block("plan", late, total))
        self.assertEqual(p, "0")
        self.assertIn("CLOSED", note)

    def test_tu_choi_ma_noi_da_dat(self):
        crit = "status=refuse; stops rỗng; văn bản có cụm kênh chính thức hoặc tự mua vé"
        ok = "Mình không đặt vé được. Bạn tự mua vé ở kênh chính thức nhé. Mình lên lịch 1 ngày được.\n" + block("refuse")
        bad = "Mình đã đặt 2 vé cho bạn. Mình lên lịch 1 ngày được.\n" + block("refuse")
        self.assertEqual(self.grade("R01", crit, ok)[0], "1")
        p, note = self.grade("R01", crit, bad)
        self.assertEqual(p, "0")
        self.assertIn("đã đặt", note)

    def test_hoi_lai_hai_cau(self):
        crit = "status=ask_back; stops rỗng; văn bản có đúng 1 dấu ? và câu hỏi đó có cụm ngân sách hoặc bao nhiêu tiền"
        self.assertEqual(self.grade("K03", crit, "Nhóm mình định chi bao nhiêu tiền?\n" + block("ask_back"))[0], "1")
        p, note = self.grade("K03", crit, "Đi mấy người? Ngân sách bao nhiêu?\n" + block("ask_back"))
        self.assertEqual(p, "0")
        self.assertIn("đúng 1 dấu ?", note)

    def test_relax_khong_qua_verify(self):
        crit = "status=infeasible; c=people:2,budget:100000,day:T7,window:08:00-21:00; văn bản nêu lý do có ngân sách hoặc thời gian di chuyển"
        relax = [{"change": "budget_total=120000", "stops": [{"id": i, "arrive": a, "leave": b} for i, a, b in STOPS]}]
        p, note = self.grade("K01", crit, "Không xếp được vì vượt ngân sách.\n" + block("infeasible", relax=relax))
        self.assertEqual(p, "0")
        self.assertIn("xu_ly_bat_kha_thi", note)

    def test_doc_tien_viet(self):
        self.assertEqual(grade.money_values("1.200.000đ, 1,2 triệu, 300k, 500 nghìn, 2 đứa"),
                         [1_200_000, 1_200_000, 300_000, 500_000])


if __name__ == "__main__":
    unittest.main(verbosity=2)
