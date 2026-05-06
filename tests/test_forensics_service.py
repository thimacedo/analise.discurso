import pytest
import json
from core.forensics_service import PasaForensicsService, VALID_CATEGORIES

@pytest.fixture
def service():
    return PasaForensicsService()

def test_get_system_prompt(service):
    prompt = service.get_system_prompt()
    assert "Sentinela Democrática" in prompt
    assert "PASA v16.4.1" in prompt
    for cat in VALID_CATEGORIES:
        assert cat in prompt

def test_parse_verdict_clean_json(service):
    raw = '{"category": "ODIO_IDENTITARIO", "confidence": 0.9, "is_hate": true, "reason": "Teste"}'
    verdict = service.parse_verdict(raw)
    assert verdict["category"] == "ODIO_IDENTITARIO"
    assert verdict["is_hate"] is True
    assert verdict["confidence"] == 0.9

def test_parse_verdict_markdown_json(service):
    raw = '```json\n{"category": "NEUTRO", "confidence": 1.0, "is_hate": false, "reason": "Livre"}\n```'
    verdict = service.parse_verdict(raw)
    assert verdict["category"] == "NEUTRO"
    assert verdict["is_hate"] is False

def test_parse_verdict_invalid_category_fallback(service):
    raw = '{"category": "XENOFOBIA_ATAQUE", "confidence": 0.8, "is_hate": true, "reason": "Teste"}'
    verdict = service.parse_verdict(raw)
    assert verdict["category"] == "XENOFOBIA_REGIONAL"

def test_audit_terms_violations(service):
    text = "O perito emitiu um laudo com provas."
    is_compliant, violations = service.audit_terms(text)
    assert is_compliant is False
    assert len(violations) == 3
    found_terms = [v['found_term'].lower() for v in violations]
    assert "perito" in found_terms
    assert "laudo" in found_terms
    assert "provas" in found_terms

def test_audit_terms_compliant(service):
    text = "O analista emitiu um dossiê com evidências situacionais."
    is_compliant, violations = service.audit_terms(text)
    assert is_compliant is True
    assert len(violations) == 0
