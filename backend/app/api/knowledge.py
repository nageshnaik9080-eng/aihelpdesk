"""Knowledge base endpoints — CRUD + semantic search (FR-7; Section 3.7).

Write operations are restricted to the Knowledge Base Administrator and System
Administrator personas (RBAC). Search/read is open to any authenticated user.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.security import Role
from app.models import User
from app.schemas import ArticleCreate, ArticleOut, ArticleUpdate, KBSearchResult
from app.services.kb_service import KBService

router = APIRouter(prefix="/kb", tags=["knowledge-base"])

_kb_writer = require_roles(Role.KB_ADMIN, Role.SYSTEM_ADMIN)


@router.get("/articles", response_model=list[ArticleOut])
async def list_articles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [ArticleOut.model_validate(a) for a in KBService(db).list()]


@router.get("/search", response_model=list[KBSearchResult])
async def search_kb(q: str = Query(..., min_length=1), top_k: int = 5,
                    user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return KBService(db).search(q, top_k=top_k)


@router.get("/articles/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ArticleOut.model_validate(KBService(db).get(article_id))


@router.post("/articles", response_model=ArticleOut, status_code=201)
async def create_article(payload: ArticleCreate, user: User = Depends(_kb_writer), db: Session = Depends(get_db)):
    return ArticleOut.model_validate(KBService(db).create(payload, author_id=user.id))


@router.put("/articles/{article_id}", response_model=ArticleOut)
async def update_article(article_id: int, payload: ArticleUpdate,
                         user: User = Depends(_kb_writer), db: Session = Depends(get_db)):
    return ArticleOut.model_validate(KBService(db).update(article_id, payload))


@router.delete("/articles/{article_id}", status_code=204)
async def delete_article(article_id: int, user: User = Depends(_kb_writer), db: Session = Depends(get_db)):
    KBService(db).delete(article_id)
