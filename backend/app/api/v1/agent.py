from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_guard import check_rate_limit
from app.core.security import extract_client_ip, hash_client_ip, verify_turnstile_token
from app.schemas.portfolio import AgentChatRequest, AgentChatResponse, AgentCitation
from app.services.rag_agent import answer_recruiter_query

router = APIRouter()


@router.post("/agent/chat", response_model=AgentChatResponse)
async def ask_shreyas_ai(
    request: Request,
    payload: AgentChatRequest,
    db: AsyncSession = Depends(get_db),
) -> AgentChatResponse:
    """Bounded recruiter assistant grounded in pgvector HNSW embeddings."""
    ip_hash = hash_client_ip(request)
    _, remaining = await check_rate_limit("agent_chat", ip_hash, limit=5, window_seconds=600)

    await verify_turnstile_token(payload.turnstile_token, extract_client_ip(request))

    result = await answer_recruiter_query(
        db,
        query=payload.query,
        category_filter=payload.category_filter,
    )
    return AgentChatResponse(
        answer=result["answer"],
        citations=[AgentCitation(**c) for c in result["citations"]],
        fallback_used=result["fallback_used"],
        remaining_queries_in_window=remaining,
    )
