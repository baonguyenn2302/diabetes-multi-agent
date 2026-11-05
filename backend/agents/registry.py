"""Lazy Agent factory: avoids loading TensorFlow/Chroma during import and mock tests."""


def build_registry():
    from agents.risk_assessment_agent import RiskAssessmentAgent
    from agents.medical_knowledge_agent import MedicalKnowledgeAgent
    # MedicalAdvisorAgent is implemented in step 3.
    registry = {
        "risk_assessment_agent": RiskAssessmentAgent(),
        "medical_knowledge_agent": MedicalKnowledgeAgent(),
    }
    try:
        from agents.medical_advisor_agent import MedicalAdvisorAgent
    except ModuleNotFoundError as exc:
        if exc.name != "agents.medical_advisor_agent":
            raise
    else:
        registry["medical_advisor_agent"] = MedicalAdvisorAgent()
    return registry
