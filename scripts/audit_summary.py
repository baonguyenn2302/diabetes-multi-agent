"""Thống kê vận hành từ logs/audit.jsonl.   python scripts/audit_summary.py [--last 100]"""
import argparse, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.agents.monitoring_agent import MonitoringAgent

ap = argparse.ArgumentParser()
ap.add_argument("--last", type=int, default=None, help="chỉ tính N request gần nhất")
a = ap.parse_args()
m = MonitoringAgent()
print(f"File log: {m.path}")
print(json.dumps(m.summary(last_n=a.last), indent=2, ensure_ascii=False))
