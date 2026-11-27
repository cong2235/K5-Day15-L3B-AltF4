"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import os

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()


_bedrock_clients = {}


def _bedrock():
    """Client bedrock-runtime dùng chung. Khoá AWS lấy từ .env (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)."""
    if "rt" not in _bedrock_clients:
        import boto3  # cài bằng: python -m pip install -r requirements.txt
        _bedrock_clients["rt"] = boto3.client(
            "bedrock-runtime", region_name=os.environ.get("AWS_DEFAULT_REGION") or "ap-southeast-2")
    return _bedrock_clients["rt"]


def call_bedrock(system, user):
    """Chat qua Amazon Bedrock (Converse API). MODEL_NAME = inference profile ID,
    vd global.anthropic.claude-haiku-4-5-20251001-v1:0 (Haiku 4.5 không gọi bằng model ID trơn)."""
    kwargs = {"modelId": MODEL_NAME,
              "messages": [{"role": "user", "content": [{"text": user}]}],
              "inferenceConfig": {"maxTokens": 1024}}
    if system:
        kwargs["system"] = [{"text": system}]
    data = _bedrock().converse(**kwargs)
    text = "".join(b.get("text", "") for b in data["output"]["message"]["content"])
    u = data["usage"]
    return {"text": text, "tokens_in": u["inputTokens"], "tokens_out": u["outputTokens"]}


def embed(text: str, dimensions: int = 1024) -> list:
    """Vector nhúng cho một đoạn chữ (Amazon Titan Text Embeddings V2). Không phải lần gọi chat nên không qua @model_call.
    Đổi model bằng EMBED_MODEL trong .env."""
    import json
    resp = _bedrock().invoke_model(
        modelId=os.environ.get("EMBED_MODEL") or "amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text, "dimensions": dimensions, "normalize": True}))
    return json.loads(resp["body"].read())["embedding"]


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    if MODEL_PROVIDER == "bedrock":
        r = call_bedrock(system, user)
        return {"text": r["text"], "model": MODEL_NAME,
                "tokens_in": int(r["tokens_in"]), "tokens_out": int(r["tokens_out"])}

    raise NotImplementedError(
        "chưa viết phần gọi model thật cho MODEL_PROVIDER=%s trong codebase/ai.py — xem docs/connect-model.md"
        % MODEL_PROVIDER)
