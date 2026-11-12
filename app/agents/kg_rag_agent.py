"""KG/RAG Agent: truy xuất tri thức tiểu đường từ Neo4j Knowledge Graph.

Quy trình (theo tài liệu kiến trúc, mục 7.2):
 1. Diễn giải câu hỏi (nhận diện ý định: triệu chứng / nguy cơ / biến chứng / chẩn đoán / phòng ngừa)
 2. Nhận diện thực thể (khớp alias không dấu, ưu tiên cụm dài nhất)
 3. Truy vấn đồ thị (láng giềng của các thực thể)
 4. (Văn bản liên quan: mô tả của thực thể)
 5. Xếp hạng bằng chứng (theo ý định)
 6. Gắn nguồn (title + url) cho MỌI bằng chứng

Agent chỉ TRUY XUẤT bằng chứng; việc diễn đạt thành câu trả lời/chat do Explanation Agent đảm nhiệm.
Kết quả là bằng chứng hỗ trợ, KHÔNG phải chẩn đoán.
"""
from typing import Callable, Optional

from app.schemas import AgentMessage
from app.text_utils import normalize_text

KB_VERSION = "kb_diabet_v1"

Q_ENTITIES = """
MATCH (e:Entity)
RETURN e.id AS id, e.name AS name, e.kind AS kind, e.description AS description,
       e.source_id AS source_id, e.search_terms AS terms
"""
Q_SOURCES = """
MATCH (s:Source)
RETURN s.id AS id, s.title AS title, s.url AS url
"""
Q_NEIGHBORS = """
MATCH (e:Entity {id: $id})-[r]-(o:Entity)
WITH r, startNode(r) AS a, endNode(r) AS b
RETURN type(r) AS relation, a.name AS a_name, a.kind AS a_kind, a.description AS a_desc,
       b.name AS b_name, b.kind AS b_kind, properties(r) AS props
"""

# (từ khóa đã bỏ dấu, các quan hệ liên quan, thực thể mặc định nếu câu hỏi không nêu thực thể nào)
INTENTS = {
    "symptom": (["trieu chung", "dau hieu", "bieu hien", "nhan biet"], ["SYMPTOM_OF"], "diabetes"),
    "risk": (["yeu to nguy co", "nguy co", "nguyen nhan", "de mac", "ai de bi", "doi tuong"],
             ["RISK_FACTOR_FOR", "MAY_PROGRESS_TO", "INCREASES_RISK_OF"], "type2"),
    "complication": (["bien chung", "hau qua", "nguy hiem", "anh huong"], ["MAY_LEAD_TO"], "diabetes"),
    "diagnosis": (["chan doan", "xet nghiem", "chi so", "nguong", "bao nhieu", "binh thuong"],
                  ["DIAGNOSES", "INDICATES", "APPLIES_TO"], "diabetes"),
    "prevention": (["phong ngua", "phong benh", "phong tranh", "du phong", "an uong", "che do an",
                    "van dong", "tap the duc", "loi khuyen", "nen lam", "lam gi", "giam can"],
                   ["HELPS_PREVENT", "HELPS_DETECT_EARLY"], "type2"),
}

REL_ORDER = ["SUBTYPE_OF", "SYMPTOM_OF", "RISK_FACTOR_FOR", "MAY_PROGRESS_TO", "INCREASES_RISK_OF",
             "MAY_LEAD_TO", "DIAGNOSES", "INDICATES", "HELPS_PREVENT", "HELPS_DETECT_EARLY",
             "APPLIES_TO", "MEASURES", "RELATES_TO"]

TEMPLATES = {
    "SUBTYPE_OF": "{a} là một thể của {b}.",
    "SYMPTOM_OF": "{a} là triệu chứng của {b}.",
    "RISK_FACTOR_FOR": "{a} là yếu tố nguy cơ của {b}.",
    "MAY_PROGRESS_TO": "{a} có thể tiến triển thành {b}.",
    "INCREASES_RISK_OF": "{a} làm tăng nguy cơ mắc {b}.",
    "MAY_LEAD_TO": "{a} có thể dẫn đến {b}.",
    "DIAGNOSES": "{a} dùng để chẩn đoán {b}: {criterion}.",
    "INDICATES": "{a} ở mức {criterion} gợi ý {b}.",
    "MEASURES": "Cột dữ liệu {a} tương ứng với {b}.",
    "RELATES_TO": "Cột dữ liệu {a} liên quan đến {b}.",
}

Runner = Callable[[str, dict], list]


class KGRAGAgent:
    NAME = "KGRAGAgent"

    def __init__(self, runner: Runner):
        """runner(cypher, params) -> list[dict]. Tách riêng để test không cần Neo4j thật."""
        self._run = runner
        self._entities: Optional[dict] = None
        self._sources: dict = {}
        self._close = lambda: None

    @classmethod
    def from_settings(cls):
        from neo4j import GraphDatabase
        from app.config import settings
        driver = GraphDatabase.driver(settings.neo4j_uri,
                                      auth=(settings.neo4j_user, settings.neo4j_password))

        def runner(cypher, params):
            records, _, _ = driver.execute_query(cypher, parameters_=params,
                                                 database_=settings.neo4j_database)
            return [r.data() for r in records]

        agent = cls(runner)
        agent._close = driver.close
        return agent

    def query(self, cypher: str, params: Optional[dict] = None) -> list[dict]:
        """Chạy truy vấn Cypher qua cùng kết nối (Rule Agent dùng để đọc ngưỡng từ KG)."""
        return self._run(cypher, params or {})

    def close(self):
        self._close()

    # ---------- chuẩn bị ----------
    def _load(self):
        if self._entities is None:
            rows = self._run(Q_ENTITIES, {})
            self._entities = {r["id"]: {**r, "terms": [t for t in (r.get("terms") or []) if t]} for r in rows}
            self._sources = {r["id"]: r for r in self._run(Q_SOURCES, {})}

    def _source(self, sid):
        s = self._sources.get(sid, {})
        return s.get("title") or "Không rõ nguồn", s.get("url") or ""

    # ---------- 1-2. Diễn giải câu hỏi & nhận diện thực thể ----------
    def detect_intents(self, question: str) -> list[str]:
        q = f" {normalize_text(question)} "
        return [name for name, (kws, _, _) in INTENTS.items() if any(f" {k} " in q for k in kws)]

    def find_entities(self, question: str) -> list[str]:
        """Khớp alias không dấu; cụm dài nhất được ưu tiên ('tiền tiểu đường' thắng 'tiểu đường')."""
        self._load()
        q = f" {normalize_text(question)} "
        spans = []
        for ent in self._entities.values():
            for t in ent["terms"]:
                pat, start = f" {t} ", 0
                while (i := q.find(pat, start)) >= 0:
                    spans.append((len(t), i + 1, i + len(pat) - 1, ent["id"]))
                    start = i + 1
        spans.sort(key=lambda s: -s[0])
        taken, found = [], []
        for _, st, en, eid in spans:
            if any(st < te and en > ts for ts, te in taken):
                continue
            taken.append((st, en))
            found.append((st, eid))
        ordered = []
        for _, eid in sorted(found):
            if eid not in ordered:
                ordered.append(eid)
        return ordered

    # ---------- 3. Truy vấn đồ thị ----------
    def _neighbors(self, entity_id: str) -> list[dict]:
        out = []
        for r in self._run(Q_NEIGHBORS, {"id": entity_id}):
            props = dict(r.get("props") or {})
            src_title, src_url = self._source(props.get("source_id"))
            a, b, rel = r["a_name"], r["b_name"], r["relation"]
            if r.get("a_kind") == "Advice":
                text = r.get("a_desc") or a
            else:
                text = TEMPLATES.get(rel, "{a} –[" + rel + "]→ {b}.").format(
                    a=a, b=b, criterion=props.get("criterion", ""))
            detail = {k: v for k, v in props.items() if k != "source_id"}
            out.append({"kind": "relation", "relation": rel, "from": a, "to": b, "text": text,
                        "detail": detail, "source_title": src_title, "source_url": src_url})
        return out

    # ---------- chạy ----------
    def run(self, request_id: str, query: str, top_k: int = 8,
            hints: Optional[list] = None) -> AgentMessage:
        """query: câu hỏi tự nhiên. hints: id thực thể ép buộc (vd Coordinator truyền ['prediabetes'])."""
        try:
            self._load()
            intents = self.detect_intents(query)
            wanted = [r for i in intents for r in INTENTS[i][1]]
            targets = [h for h in (hints or []) if h in self._entities]
            for e in self.find_entities(query):
                if e not in targets:
                    targets.append(e)
            default = next((INTENTS[i][2] for i in intents), "diabetes")
            if not targets:
                targets = [default]

            rows = [r for t in targets for r in self._neighbors(t)]
            if wanted and not any(r["relation"] in wanted for r in rows) and default not in targets:
                targets.append(default)
                rows += self._neighbors(default)

            # loại trùng + xếp hạng: quan hệ đúng ý định trước, sau đó theo REL_ORDER
            seen, uniq = set(), []
            for r in rows:
                key = (r["relation"], r["from"], r["to"])
                if key not in seen:
                    seen.add(key)
                    uniq.append(r)
            uniq.sort(key=lambda r: (0 if r["relation"] in wanted else 1,
                                     REL_ORDER.index(r["relation"]) if r["relation"] in REL_ORDER else 99))

            evidence = []
            for t in targets[:2]:                      # mô tả (văn bản) của tối đa 2 thực thể chính
                e = self._entities[t]
                title, url = self._source(e.get("source_id"))
                evidence.append({"kind": "description", "relation": None, "from": e["name"], "to": None,
                                 "text": e.get("description") or e["name"], "detail": {},
                                 "source_title": title, "source_url": url})
            shown = {e["text"] for e in evidence}          # tránh lặp lại đúng nội dung đã nêu ở phần mô tả
            evidence += [r for r in uniq if r["text"] not in shown][:top_k]

            return AgentMessage.ok(
                request_id, self.NAME,
                payload={"matched_entities": [self._entities[t]["name"] for t in targets],
                         "entity_ids": targets, "intents": intents,
                         "n_relations": len(uniq), "n_returned": len(evidence)},
                evidence=evidence, version=KB_VERSION)
        except Exception as e:
            return AgentMessage.fail(request_id, self.NAME, f"{type(e).__name__}: {e}", KB_VERSION)


def format_context(evidence: list[dict]) -> str:
    """Biến bằng chứng thành khối văn bản có đánh số nguồn – dùng làm ngữ cảnh cho LLM/Explanation Agent."""
    lines = []
    for i, ev in enumerate(evidence, 1):
        src = ev["source_title"] + (f" ({ev['source_url']})" if ev["source_url"] else "")
        lines.append(f"[{i}] {ev['text']}  — Nguồn: {src}")
    return "\n".join(lines)
