from src.config import APP_ENV
from src.okf.loader import load_documents, search_documents
from src.prompts.templates import build_prompt


def test_config_loaded():
    assert APP_ENV is not None


def test_knowledge_documents_load():
    documents = load_documents()

    assert len(documents) > 0


def test_search_finds_ceo_information():
    results = search_documents("Who is the CEO of Try Soft AI?")

    assert len(results) > 0
    assert any(
        "ceo" in document["content"].lower()
        for document in results
    )


def test_search_finds_company_information():
    results = search_documents("What services does Try Soft AI provide?")

    assert len(results) > 0


def test_grounded_prompt_contains_question():
    prompt = build_prompt(
        prompt_type="grounded",
        knowledge_context="Try Soft AI provides software development services.",
        question="What services does Try Soft AI provide?",
    )

    assert "What services does Try Soft AI provide?" in prompt


def test_concise_prompt():
    prompt = build_prompt(
        prompt_type="concise",
        knowledge_context="Try Soft AI provides AI services.",
        question="What does Try Soft AI provide?",
    )

    assert "What does Try Soft AI provide?" in prompt


def test_structured_prompt():
    prompt = build_prompt(
        prompt_type="structured",
        knowledge_context="Try Soft AI provides AI services.",
        question="What does Try Soft AI provide?",
    )

    assert "What does Try Soft AI provide?" in prompt

def test_health_endpoint():
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_redis_get():
    from unittest.mock import MagicMock, patch
    from src.cache.redis_service import RedisService

    with patch("src.cache.redis_service.redis.Redis") as mock_redis:
        mock_client = MagicMock()
        mock_client.get.return_value = "cached response"
        mock_redis.return_value = mock_client

        service = RedisService()

        result = service.get("test-key")

        assert result == "cached response"
        mock_client.get.assert_called_once_with("test-key")


def test_redis_set():
    from unittest.mock import MagicMock, patch
    from src.cache.redis_service import RedisService

    with patch("src.cache.redis_service.redis.Redis") as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        service = RedisService()

        service.set("test-key", "test-value", expire=60)

        mock_client.set.assert_called_once_with(
            "test-key",
            "test-value",
            ex=60,
        )


def test_redis_delete():
    from unittest.mock import MagicMock, patch
    from src.cache.redis_service import RedisService

    with patch("src.cache.redis_service.redis.Redis") as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        service = RedisService()

        service.delete("test-key")

        mock_client.delete.assert_called_once_with("test-key")


def test_redis_ping():
    from unittest.mock import MagicMock, patch
    from src.cache.redis_service import RedisService

    with patch("src.cache.redis_service.redis.Redis") as mock_redis:
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client

        service = RedisService()

        assert service.ping() is True

def test_groq_service_initialization():
    from unittest.mock import patch
    from src.llm.groq_service import GroqService

    with patch("src.llm.groq_service.Groq") as mock_groq:
        service = GroqService()

        mock_groq.assert_called_once()
        assert service.client is mock_groq.return_value


def test_groq_generate_response():
    from unittest.mock import MagicMock, patch
    from src.llm.groq_service import GroqService

    with patch("src.llm.groq_service.Groq") as mock_groq:
        mock_client = MagicMock()

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"

        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client

        service = GroqService()

        result = service.generate_response("Test question")

        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()

def test_chat_cache_hit():
    from unittest.mock import MagicMock, patch
    from src.api.chat import chat
    from src.api.schemas import ChatRequest

    mock_db = MagicMock()

    mock_conversation = MagicMock()
    mock_conversation.id = 1

    mock_redis = MagicMock()
    mock_redis.get.return_value = "Cached answer"

    with patch("src.api.chat.SessionLocal", return_value=mock_db), \
         patch(
             "src.api.chat.get_or_create_conversation",
             return_value=mock_conversation,
         ), \
         patch("src.api.chat.redis_service", mock_redis):

        request = ChatRequest(
            session_id="test-session",
            message="Who is the CEO of Try Soft AI?",
        )

        response = chat(request)

        assert response.session_id == "test-session"
        assert response.response == "Cached answer"

        mock_redis.get.assert_called_once()
        mock_redis.set.assert_not_called()
        mock_db.close.assert_called_once()
