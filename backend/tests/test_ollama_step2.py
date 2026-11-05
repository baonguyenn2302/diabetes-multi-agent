"""Offline tests: no Ollama server or TensorFlow needed."""
import json
import tempfile
import unittest
from pathlib import Path
from agents.coordinator import Coordinator
from services.ollama_service import OllamaService, OllamaUnavailable

class FakeAgent:
    def __init__(self, name, result):
        self.name, self.result, self.calls = name, result, []
    def run(self, task):
        self.calls.append(task)
        return {'session_id': task['session_id'], 'task_id': task['task_id'],
                'agent': self.name, 'status': 'success', 'result': self.result, 'error': None}

class FakeOllama:
    def __init__(self, intent='knowledge', summary='Tóm tắt từ nguồn kiểm thử.'):
        self.intent, self.summary, self.classifications, self.summaries = intent, summary, [], []
    def classify_intent(self, message):
        self.classifications.append(message)
        return self.intent
    def summarize(self, question, sources, prediction_text):
        self.summaries.append((question, sources, prediction_text))
        return self.summary

class Step2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        meta = Path(self.temp.name)/'meta.json'
        meta.write_text(json.dumps({'input_fields':['age','bmi']}), encoding='utf-8')
        self.meta = meta
        self.knowledge = FakeAgent('medical_knowledge_agent', {'sources':[{'excerpt':'Tài liệu thử nghiệm về tiểu đường', 'source_title':'Nguồn test'}]})
        self.risk = FakeAgent('risk_assessment_agent', {'prediction':0,'probability':.2})
        self.advisor = FakeAgent('medical_advisor_agent', {'warnings':[]})
        self.agents = {a.name:a for a in (self.knowledge,self.risk,self.advisor)}
    def tearDown(self): self.temp.cleanup()
    def test_clear_request_uses_rule_not_llm_classification(self):
        llm = FakeOllama()
        result = Coordinator(self.agents,self.meta,ollama=llm).run('Tiểu đường type 2 là gì?')
        self.assertEqual(result['status'],'success')
        self.assertFalse(llm.classifications)
        self.assertEqual(len(llm.summaries),1)
        self.assertEqual(result['answer'],'Tóm tắt từ nguồn kiểm thử.')
    def test_ambiguous_request_uses_llm_allowlist_intent(self):
        llm = FakeOllama(intent='symptoms')
        result = Coordinator(self.agents,self.meta,ollama=llm).run('Mình hay thấy khô miệng, nên hiểu thế nào?')
        self.assertEqual(result['intent'],'symptoms')
        self.assertEqual(len(self.risk.calls),0)
        self.assertEqual(len(self.advisor.calls),1)
    def test_out_of_scope_skips_agents(self):
        llm = FakeOllama(intent='out_of_scope')
        result = Coordinator(self.agents,self.meta,ollama=llm).run('Hướng dẫn chơi cờ vua')
        self.assertEqual(result['intent'],'out_of_scope')
        self.assertEqual(len(self.knowledge.calls),0)
    def test_llm_failure_keeps_grounded_excerpts(self):
        class Broken(FakeOllama):
            def summarize(self,*args): raise OllamaUnavailable('offline')
        result = Coordinator(self.agents,self.meta,ollama=Broken()).run('Tiểu đường là gì?')
        self.assertIn('Tài liệu thử nghiệm',result['answer'])
        self.assertTrue(any('Ollama' in w for w in result['warnings']))
    def test_no_sources_does_not_call_llm(self):
        self.knowledge.result={'sources':[]}
        llm=FakeOllama()
        Coordinator(self.agents,self.meta,ollama=llm).run('Tiểu đường là gì?')
        self.assertEqual(len(llm.summaries),0)
    def test_llm_malformed_intent_rejected(self):
        llm=OllamaService(model='test')
        llm.generate=lambda *args, **kwargs: '{"intent":"execute_python"}'
        with self.assertRaises(OllamaUnavailable): llm.classify_intent('test')

if __name__=='__main__': unittest.main()
