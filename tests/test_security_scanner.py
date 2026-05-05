import pytest
from core.security_scanner import SecurityScanner

@pytest.fixture
def scanner():
    return SecurityScanner()

def test_cpf_masking(scanner):
    text = "Meu CPF é 123.456.789-00 e o outro é 98765432100"
    masked = scanner.mask_sensitive_data(text)
    assert "[REDACTED_CPF]" in masked
    assert "123.456.789-00" not in masked
    assert "98765432100" not in masked

def test_cnpj_masking(scanner):
    text = "Empresa: 12.345.678/0001-99"
    masked = scanner.mask_sensitive_data(text)
    assert "[REDACTED_CNPJ]" in masked
    assert "12.345.678/0001-99" not in masked

def test_phone_masking(scanner):
    text = "Me liga em +55 11 98888-7777 ou 1188887777"
    masked = scanner.mask_sensitive_data(text)
    assert "[REDACTED_Phone_BR]" in masked
    assert "98888-7777" not in masked
    assert "1188887777" not in masked

def test_credit_card_masking(scanner):
    text = "Paguei com o cartão 1234-5678-9012-3456"
    masked = scanner.mask_sensitive_data(text)
    assert "[REDACTED_Credit_Card]" in masked
    assert "1234-5678-9012-3456" not in masked

def test_secret_key_masking(scanner):
    text = "Minha chave falsa do Google é AIzaSyB_1234567890abcdefghijklmnopqrstuv"
    masked = scanner.mask_sensitive_data(text)
    assert "[REDACTED_Secret_Key]" in masked
    assert "AIzaSyB_" not in masked

def test_ssh_key_masking(scanner):
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA7...\n-----END RSA PRIVATE KEY-----"
    masked = scanner.mask_sensitive_data(text)
    assert "[REDACTED_SSH_Private_Key]" in masked

def test_no_sensitive_data(scanner):
    text = "Este é um texto comum sem nada demais."
    masked = scanner.mask_sensitive_data(text)
    assert masked == text
