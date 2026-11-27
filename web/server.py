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
from agent import answer  # noqa: E402

MAX_BODY = 16 * 1024
MAX_TEXT = 2000
MAX_SESSIONS = 500
BLOCK = re.compile(r"```json\s*(\{.*\})\s*```\s*$", re.S)
SESSION_ID = re.compile(r"[A-Za-z0-9-]{8,64}")
LOCK = threading.Lock()  # tracing giữ trạng thái chung, nên mỗi lúc chỉ chạy một lượt
SESSIONS: OrderedDict = OrderedDict()  # mã phiên → Turn của lượt gần nhất (nằm trong bộ nhớ, tắt máy chủ là mất)


def run_turn(text: str, session: str | None) -> dict:
    with LOCK:
        prev = SESSIONS.get(session) if session else None
        tracing.begin("web")
        try:
            res = answer(text, prev)
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
    }


class Handler(SimpleHTTPRequestHandler):
    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
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
