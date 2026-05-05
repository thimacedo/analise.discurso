import pytest
import os
import sys

# Add the project root to the path so we can import core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pasa_auditor import PASAAuditor

def test_pasa_auditor_compliant_text():
    auditor = PASAAuditor()
    result = auditor.audit_text("O relatório contém dados e sinais da análise situacional.")
    assert result["is_compliant"] is True
    assert len(result["violations"]) == 0

def test_pasa_auditor_forbidden_pericia():
    auditor = PASAAuditor()
    result = auditor.audit_text("Foi realizada uma perícia técnica no sistema.")
    assert result["is_compliant"] is False
    assert len(result["violations"]) == 1
    assert result["violations"][0]["found_term"].lower() == "perícia"
    assert result["violations"][0]["suggested_replacement"] == "Análise"

def test_pasa_auditor_forbidden_forense():
    auditor = PASAAuditor()
    result = auditor.audit_text("Os dados da munição FORENSE confirmam o ataque.")
    assert result["is_compliant"] is False
    assert result["violations"][0]["found_term"].lower() == "forense"
    assert "Estratégica" in result["violations"][0]["suggested_replacement"]

def test_pasa_auditor_forbidden_prova():
    auditor = PASAAuditor()
    result = auditor.audit_text("A prova do crime foi encontrada nos logs.")
    assert result["is_compliant"] is False
    assert result["violations"][0]["found_term"].lower() == "prova"
    assert "Dados / Sinais" in result["violations"][0]["suggested_replacement"]

def test_pasa_auditor_multiple_violations():
    auditor = PASAAuditor()
    result = auditor.audit_text("O perito encontrou a prova forense.")
    assert result["is_compliant"] is False
    assert len(result["violations"]) == 3
    found_terms = [v["found_term"].lower() for v in result["violations"]]
    assert "perito" in found_terms
    assert "forense" in found_terms
    assert "prova" in found_terms
