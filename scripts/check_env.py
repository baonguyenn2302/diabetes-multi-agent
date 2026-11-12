"""Kiểm tra môi trường. Chạy:  python scripts/check_env.py"""
import sys, importlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ok_all = True
def check(label, cond, hint=""):
    global ok_all
    print(f"[{'OK' if cond else 'FAIL'}] {label}" + ("" if cond else f"  -> {hint}"))
    ok_all &= bool(cond)

check("Python >= 3.10", sys.version_info >= (3, 10), f"đang dùng {sys.version.split()[0]}")

for mod in ["pydantic", "dotenv", "pytest", "numpy", "pandas", "sklearn", "joblib", "tensorflow"]:
    try:
        importlib.import_module(mod); check(f"import {mod}", True)
    except ImportError:
        check(f"import {mod}", False, "chạy: pip install -r requirements.txt")

for d in ["app/agents", "models", "kb", "sim", "logs", "ui", "tests", "scripts"]:
    check(f"thư mục {d}/", (ROOT / d).is_dir(), "thiếu thư mục")

try:
    from app.config import settings
    from app.schemas import AgentMessage
    m = AgentMessage.ok("req_test", "SmokeAgent", {"hello": 1})
    check("app.config + app.schemas hoạt động", m.status == "ok")
except Exception as e:
    check("app.config + app.schemas hoạt động", False, str(e))

print("\n=> KẾT QUẢ:", "TẤT CẢ OK ✅" if ok_all else "CÓ LỖI ❌ (xem các dòng FAIL)")
sys.exit(0 if ok_all else 1)
