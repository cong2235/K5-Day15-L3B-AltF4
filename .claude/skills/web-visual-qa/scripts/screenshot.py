"""Chụp màn hình một trang HTML ở nhiều độ rộng bằng Chrome/Edge headless.

    python screenshot.py web/index.html [--widths 1366,1440,1920] [--height 900] [--full [--full-height 6000]] [--query id=x] [--out DIR]

Chỉ dùng thư viện chuẩn. In ra đường dẫn từng file PNG.
"""
import argparse
import functools
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse

CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def find_browser():
    for c in CANDIDATES:
        if not c:
            continue
        path = c if os.path.isfile(c) else shutil.which(c)
        if path:
            return path
    sys.exit("Không tìm thấy Chrome/Edge. Đặt biến CHROME_PATH tới file chạy của trình duyệt.")


def serve(root):
    handler = functools.partial(_QuietHandler, directory=root)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def shoot(browser, url, width, height, out_png, profile):
    cmd = [
        browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--no-first-run", "--no-default-browser-check",
        "--user-data-dir=" + profile,
        "--virtual-time-budget=4000",
        "--window-size=%d,%d" % (width, height),
        "--screenshot=" + out_png, url,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    if not os.path.isfile(out_png):
        sys.exit("Chụp thất bại ở %dx%d: %s" % (width, height, " ".join(cmd)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--widths", default="1366,1440,1920")
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--full-height", type=int, default=6000)
    ap.add_argument("--query", default="", help="chuỗi truy vấn thêm vào URL, vd id=my-khe")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "web-visual-qa"))
    a = ap.parse_args()

    page = os.path.abspath(a.page)
    if not os.path.isfile(page):
        sys.exit("Không thấy file: " + page)
    os.makedirs(a.out, exist_ok=True)
    browser = find_browser()
    httpd = serve(os.path.dirname(page))
    url = "http://127.0.0.1:%d/%s" % (httpd.server_address[1], urllib.parse.quote(os.path.basename(page)))
    stem = os.path.splitext(os.path.basename(page))[0]
    if a.query:
        url += "?" + a.query
        stem += "-" + "".join(c if c.isalnum() else "-" for c in a.query)
    profile = tempfile.mkdtemp(prefix="wvqa-profile-")
    try:
        for w in [int(x) for x in a.widths.split(",")]:
            sizes = [(a.height, "")] + ([(a.full_height, "-full")] if a.full else [])
            for h, tag in sizes:
                out_png = os.path.join(a.out, "%s-%d%s.png" % (stem, w, tag))
                shoot(browser, url, w, h, out_png, profile)
                print(out_png)
    finally:
        httpd.shutdown()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
