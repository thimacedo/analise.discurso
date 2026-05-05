import pytest
from core.pasa_auditor import PASAAuditor

@pytest.fixture
def auditor():
    return PASAAuditor()

def test_pasa_compliant_text(auditor):
    text = "A análise situacional concluiu que os dados indicam atividade anômala no relatório."
    is_compliant, violations = auditor.audit_text(text)
    assert is_compliant is True
    assert len(violations) == 0

def test_pasa_forbidden_pericia(auditor):
    text = "Realizamos uma PERÍCIA técnica nos sistemas."
    is_compliant, violations = auditor.audit_text(text)
    assert is_compliant is False
    assert len(violations) == 1
    assert violations[0]['found_term'].lower() == "perícia"

def test_pasa_forbidden_forense_and_prova(auditor):
    text = "A prova forense é irrefutável."
    is_compliant, violations = auditor.audit_text(text)
    assert is_compliant is False
    assert len(violations) == 2
    terms = [v['found_term'].lower() for v in violations]
    assert "prova" in terms
    assert "forense" in terms

def test_pasa_forbidden_laudo(auditor):
    text = "O LAUDO aponta irregularidades."
    is_compliant, violations = auditor.audit_text(text)
    assert is_compliant is False
    assert len(violations) == 1
    assert violations[0]['found_term'].lower() == "laudo"

def test_pasa_word_boundaries(auditor):
    # 'comprovante' contains 'prova' but shouldn't be flagged due to word boundaries
    text = "O comprovante de pagamento foi enviado."
    is_compliant, violations = auditor.audit_text(text)
    assert is_compliant is True
    assert len(violations) == 0