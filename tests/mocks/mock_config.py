# tests/mocks/mock_config.py

class MockSettings:
    SUPABASE_URL: str = "http://mock-supabase.com"
    SUPABASE_KEY: str = "mock-key"
    # Adicionar outras configurações se fetch_pending.py as usar diretamente (não usa no momento)
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    IA_PROVIDER: str = "mock"

settings = MockSettings()
