from fastapi import APIRouter
from sqlalchemy.orm import Session

from src.api.schemas import ChatRequest, ChatResponse
from src.cache.redis_service import RedisService
from src.database.connection import SessionLocal
from src.database.models import Conversation, Message
from src.llm.groq_service import GroqService
from src.okf.loader import search_documents
from src.prompts.templates import build_prompt


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


groq_service = GroqService()
redis_service = RedisService()


def get_or_create_conversation(
    db: Session,
    session_id: str,
) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .first()
    )

    if conversation:
        return conversation

    conversation = Conversation(
        session_id=session_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    db = SessionLocal()

    try:
        conversation = get_or_create_conversation(
            db,
            request.session_id,
        )

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )

        db.add(user_message)
        db.commit()

        cache_key = f"chat:{request.message.strip().lower()}"

        cached_response = redis_service.get(cache_key)

        if cached_response:
            response = cached_response

        else:
            documents = search_documents(request.message)

            knowledge_context = "\n\n".join(
                document["content"]
                for document in documents
            )

            prompt = build_prompt(
                prompt_type="grounded",
                knowledge_context=knowledge_context,
                question=request.message,
            )

            response = groq_service.generate_response(prompt)

            redis_service.set(
                cache_key,
                response,
                expire=3600,
            )

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response,
        )

        db.add(assistant_message)
        db.commit()

        return ChatResponse(
            session_id=request.session_id,
            response=response,
        )

    finally:
        db.close()