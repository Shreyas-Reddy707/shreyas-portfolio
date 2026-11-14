from fastapi import APIRouter

from app.api.v1 import agent, contact, public, webhooks

api_router = APIRouter()
api_router.include_router(public.router, tags=["public"])
api_router.include_router(contact.router, tags=["contact"])
api_router.include_router(webhooks.router, tags=["webhooks"])
api_router.include_router(agent.router, tags=["agent"])

