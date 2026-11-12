"""Hỏi thử KG/RAG Agent trên Neo4j thật.
    python scripts/try_kb.py                       # chạy các câu hỏi mẫu
    python scripts/try_kb.py "Triệu chứng tiểu đường là gì?"
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.agents.kg_rag_agent import KGRAGAgent

SAMPLES = ["Triệu chứng của tiểu đường là gì?",
           "Chỉ số HbA1c bao nhiêu thì bị tiền tiểu đường?",
           "Những ai dễ bị tiểu đường type 2?",
           "Tôi nên ăn uống và vận động thế nào để phòng bệnh?",
           "Biến chứng của tiểu đường nguy hiểm không?"]
questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else SAMPLES

agent = KGRAGAgent.from_settings()
try:
    for q in questions:
        msg = agent.run("req_try", q, top_k=6)
        print("\n" + "=" * 70 + f"\nCâu hỏi: {q}")
        if msg.status != "ok":
            print("LỖI:", msg.error); continue
        print(f"Thực thể: {msg.payload['matched_entities']} | ý định: {msg.payload['intents']}")
        for i, ev in enumerate(msg.evidence, 1):
            print(f" [{i}] {ev['text']}\n      ↳ {ev['source_title']} | {ev['source_url']}")
finally:
    agent.close()
