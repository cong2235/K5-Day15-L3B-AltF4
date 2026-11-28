"""Máy chủ thử cho website: phục vụ web/ và nối ô chat với codebase/agent.answer().

Chạy:  python web/server.py            → http://localhost:8000
       python web/server.py 8080       → đổi cổng
Chỉ nghe ở 127.0.0.1. Khoá model nằm trong .env ở máy chủ, trình duyệt không bao giờ thấy.
Chỉ dùng thư viện chuẩn của Python (Bedrock thì cần boto3 như bản chạy thử).
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import urllib.parse
import urllib.request
from collections import OrderedDict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

WEB = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(WEB), "codebase"))
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import ai  # noqa: E402
import tracing  # noqa: E402
from agent import answer_options, choose  # noqa: E402

MAX_BODY = 16 * 1024
MAX_TEXT = 2000
MAX_SESSIONS = 500
BLOCK = re.compile(r"```json\s*(\{.*\})\s*```\s*$", re.S)
SESSION_ID = re.compile(r"[A-Za-z0-9-]{8,64}")
LOCK = threading.Lock()  # tracing giữ trạng thái chung, nên mỗi lúc chỉ chạy một lượt
SESSIONS: OrderedDict = OrderedDict()  # mã phiên → Turn của lượt gần nhất (nằm trong bộ nhớ, tắt máy chủ là mất)


# ---------------------------------------------------------------- tuyến đường bộ cho bản đồ (OSRM)
# Máy chủ gọi OSRM thay trình duyệt: không bị tiện ích chặn quảng cáo chặn, có lưu đệm, chờ được lâu hơn.
# Chỉ nhận toạ độ trong vùng Đà Nẵng – Hội An để endpoint này không thành proxy mở.
OSRM = "https://router.project-osrm.org/route/v1/driving/"
ROUTE_CACHE: OrderedDict = OrderedDict()
MAX_ROUTE_POINTS = 8
BBOX = (15.6, 16.35, 107.85, 108.45)   # lat min, lat max, lon min, lon max


def _points(raw: str) -> list[tuple[float, float]] | None:
    pts = []
    for part in raw.split(";"):
        try:
            lat, lon = (float(x) for x in part.split(","))
        except ValueError:
            return None
        if not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lon <= BBOX[3]):
            return None
        pts.append((round(lat, 5), round(lon, 5)))
    return pts if 2 <= len(pts) <= MAX_ROUTE_POINTS else None


def road_route(pts: list[tuple[float, float]]) -> dict | None:
    key = tuple(pts)
    if key in ROUTE_CACHE:
        return ROUTE_CACHE[key]
    url = OSRM + ";".join("%s,%s" % (lon, lat) for lat, lon in pts) + "?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={"User-Agent": "AltF4-demo/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            body = json.loads(r.read())
        route = body["routes"][0]
        out = {"line": [[lat, lon] for lon, lat in route["geometry"]["coordinates"]],
               "km": round(route["distance"] / 1000, 1)}
    except Exception as e:  # mạng, OSRM giới hạn lượt, dữ liệu lạ: trình duyệt sẽ nối nét đứt
        print("[route] %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return None
    ROUTE_CACHE[key] = out
    while len(ROUTE_CACHE) > 500:
        ROUTE_CACHE.popitem(last=False)
    return out


def run_turn(text: str, session: str | None) -> dict:
    with LOCK:
        prev = SESSIONS.get(session) if session else None
        tracing.begin("web")
        try:
            res = answer_options(text, prev)
        finally:
            summary, _ = tracing.end()
        if session:
            SESSIONS[session] = res.get("turn")
            SESSIONS.move_to_end(session)
            while len(SESSIONS) > MAX_SESSIONS:
                SESSIONS.popitem(last=False)
    out = res["output"]
    m = BLOCK.search(out)
    return {
        "text": out[:m.start()].rstrip() if m else out,
        "result": json.loads(m.group(1)) if m else None,
        "meta": {k: summary[k] for k in ("models", "model_calls", "tokens_in", "tokens_out")},
        "editing": bool(res.get("turn") and res["turn"].constraints),
        "options": res.get("options") or [],
        "understood": res.get("understood"),
        "notes": res.get("notes") or [],
        "checked_on": res.get("checked_on"),
    }


def choose_option(session: str, index: int) -> bool:
    """Người dùng bấm chọn một phương án: lịch đó thành nền cho tin nhắn sửa tiếp theo."""
    with LOCK:
        turn = SESSIONS.get(session)
        if turn is None or not getattr(turn, "options", ()) or not 0 <= index < len(turn.options):
            return False
        SESSIONS[session] = choose(turn, index)
        return True


class Handler(SimpleHTTPRequestHandler):
    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path.startswith("/api/route"):
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            pts = _points((query.get("c") or [""])[0])
            if pts is None:
                self._json(400, {"error": "Toạ độ không hợp lệ."})
                return
            route = road_route(pts)
            self._json(200 if route else 502, route or {"error": "Chưa lấy được đường bộ."})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/choose":
            try:
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(min(length, MAX_BODY)) or b"{}")
                session, index = str(body.get("session") or ""), int(body.get("index"))
            except (ValueError, TypeError, AttributeError):
                self._json(400, {"error": "Yêu cầu không đọc được."})
                return
            ok = SESSION_ID.fullmatch(session) is not None and choose_option(session, index)
            self._json(200 if ok else 404, {"ok": ok})
            return
        if self.path != "/api/chat":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                raise ValueError("quá dài")
            body = json.loads(self.rfile.read(length) or b"{}")
            text = str(body.get("message", "")).strip()[:MAX_TEXT]
            session = str(body.get("session") or "")
        except (ValueError, AttributeError):
            self._json(400, {"error": "Yêu cầu không đọc được."})
            return
        session = session if SESSION_ID.fullmatch(session) else None
        if not text:
            self._json(400, {"error": "Bạn chưa gõ gì."})
            return
        try:
            self._json(200, run_turn(text, session))
        except Exception as e:  # lỗi gọi model (mạng, key, hết lượt): ghi ở máy chủ, báo ngắn cho người dùng
            print("[lỗi] %s: %s" % (type(e).__name__, e), file=sys.stderr)
            self._json(502, {"error": "Trợ lý đang gặp lỗi khi gọi AI. Bạn thử lại sau ít phút nhé."})


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=WEB))
    print("Website: http://localhost:%d  ·  model: %s" % (port, ai.MODEL_PROVIDER if ai.MODEL_PROVIDER != "fake"
                                                          else "fake (chưa nối model, xem .env)"))
    print("Dừng: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
