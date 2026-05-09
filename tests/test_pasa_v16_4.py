import pytest
from core.pasa_auditor import PASAAuditor

@pytest.fixture
def auditor():
    return PASAAuditor()

@pytest.mark.asyncio
async def test_pasa_v16_4_rigor_criminal(auditor):
    # Test for criminal imputation
    text = "Esse político é um ladrão corrupto chefe de quadrilha."
    result = await auditor.process(text)
    assert result["is_hate"] is True
    assert result["category"] == "RIGOR_CRIMINAL"

@pytest.mark.asyncio
async def test_pasa_v16_4_institucional(auditor):
    # Test for institutional attack
    text = "A ditadura da toga do Xandão fraudou as urnas."
    result = await auditor.process(text)
    assert result["is_hate"] is True
    assert result["category"] == "ATAQUE_INSTITUCIONAL"

@pytest.mark.asyncio
async def test_pasa_v16_4_desumanizacao(auditor):
    # Test for dehumanization
    text = "Eles são uns ratos, lixo humano."
    result = await auditor.process(text)
    assert result["is_hate"] is True
    assert result["category"] == "INSULTO_AD_HOMINEM"

@pytest.mark.asyncio
async def test_pasa_v16_4_ironia(auditor):
    # Test for irony (sarcasm scanner)
    text = "Parabéns pelo roubo."
    result = await auditor.process(text)
    assert result["is_hate"] is True
    assert result["category"] == "RIGOR_CRIMINAL"

@pytest.mark.asyncio
async def test_pasa_v16_4_ameaca(auditor):
    text = "Vou te matar na rua, tem que levar tiro no paredão."
    result = await auditor.process(text)
    assert result["is_hate"] is True
    assert result["category"] == "AMEACA"

@pytest.mark.asyncio
async def test_pasa_compliant(auditor):
    text = "O candidato apresentou suas propostas."
    result = await auditor.process(text)
    assert result["is_hate"] is False
    assert result["category"] == "NEUTRO"
