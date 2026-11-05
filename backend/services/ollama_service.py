"""Local Ollama client. Python standard library only; no cloud LLM calls."""
from __future__ import annotations
import json
import os
from pathlib import Path
from urllib import request, error

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

class OllamaUnavailable(RuntimeError):
    pass

class OllamaService:
    def __init__(self, base_url=None, model=None, timeout=None):
        self.base_url = (base_url or os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')).rstrip('/')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        self.timeout = float(timeout if timeout is not None else os.getenv('OLLAMA_TIMEOUT', '90'))
        if not (self.base_url.startswith('http://127.0.0.1:') or self.base_url.startswith('http://localhost:')):
            raise ValueError('MVP chỉ cho phép Ollama chạy local trên localhost/127.0.0.1')

    def generate(self, prompt: str, system: str, json_mode=False) -> str:
        payload = {'model': self.model, 'prompt': prompt, 'system': system,
                   'stream': False, 'options': {'temperature': 0}}
        if json_mode:
            payload['format'] = 'json'
        req = request.Request(self.base_url + '/api/generate', data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                              headers={'Content-Type':'application/json'}, method='POST')
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                obj = json.loads(response.read().decode('utf-8'))
        except (error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise OllamaUnavailable(f'Không gọi được Ollama local: {exc}') from exc
        if not isinstance(obj, dict) or not isinstance(obj.get('response'), str) or not obj['response'].strip():
            raise OllamaUnavailable('Ollama trả về response trống hoặc không hợp lệ')
        return obj['response'].strip()

    def classify_intent(self, message: str) -> str:
        system = (PROMPTS_DIR / 'coordinator_prompt.txt').read_text(encoding='utf-8')
        raw = self.generate('Câu hỏi người dùng:\n' + message, system=system, json_mode=True)
        try:
            data = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise OllamaUnavailable('Ollama không trả JSON hợp lệ') from exc
        intent = data.get('intent') if isinstance(data, dict) else None
        if intent not in ('knowledge', 'symptoms', 'risk', 'out_of_scope'):
            raise OllamaUnavailable('Ollama phân loại ngoài allowlist')
        return intent

    def summarize(self, question: str, excerpts: list[dict], prediction_text: str = '') -> str:
        if not excerpts:
            raise ValueError('Không có nguồn; không cho LLM tự tạo lời tư vấn')
        system = (PROMPTS_DIR / 'answer_prompt.txt').read_text(encoding='utf-8')
        passages = [{
            'title': e.get('source_title', ''),
            'excerpt': (e.get('full_text') or e.get('excerpt') or '')[:1500],
        } for e in excerpts[:4]]
        prompt = json.dumps({'question': question[:2000], 'prediction_summary': prediction_text[:1000], 'sources': passages}, ensure_ascii=False)
        return self.generate(prompt, system=system)
