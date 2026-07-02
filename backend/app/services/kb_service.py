"""Knowledge base service (FR-6, FR-7; Section 3.7).

CRUD over articles in SQLite + (re)indexing their chunks into the vector store so
the RAG pipeline retrieves current content. Naive paragraph chunking for the MVP.
"""
from __future__ import annotations

from fastapi import HTTPException, status

from app.core.vectorstore import add_kb_chunks, delete_kb_article, search_kb
from app.models import KnowledgeArticle
from app.repositories.article_repo import ArticleRepository
from app.schemas import ArticleCreate, ArticleUpdate, KBSearchResult


def _chunk(text: str, max_len: int = 600) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    for para in paras or [text]:
        if len(para) <= max_len:
            chunks.append(para)
        else:
            for i in range(0, len(para), max_len):
                chunks.append(para[i:i + max_len])
    return chunks or [text]


class KBService:
    def __init__(self, db) -> None:
        self.articles = ArticleRepository(db)

    def _index(self, article: KnowledgeArticle) -> None:
        delete_kb_article(article.id)  # clear stale chunks first
        items = [
            (f"art-{article.id}-{i}", chunk,
             {"article_id": article.id, "title": article.title, "category": article.category})
            for i, chunk in enumerate(_chunk(article.content))
        ]
        add_kb_chunks(items)

    def create(self, payload: ArticleCreate, author_id: int | None) -> KnowledgeArticle:
        article = self.articles.add(KnowledgeArticle(
            title=payload.title, content=payload.content,
            category=payload.category, author_id=author_id,
        ))
        self._index(article)
        return article

    def update(self, article_id: int, payload: ArticleUpdate) -> KnowledgeArticle:
        article = self.articles.get(article_id)
        if not article:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.")
        if payload.title is not None:
            article.title = payload.title
        if payload.content is not None:
            article.content = payload.content
        if payload.category is not None:
            article.category = payload.category
        article = self.articles.save(article)
        self._index(article)
        return article

    def delete(self, article_id: int) -> None:
        article = self.articles.get(article_id)
        if not article:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.")
        delete_kb_article(article_id)
        self.articles.delete(article)

    def list(self) -> list[KnowledgeArticle]:
        return self.articles.list()

    def get(self, article_id: int) -> KnowledgeArticle:
        article = self.articles.get(article_id)
        if not article:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.")
        return article

    def search(self, query: str, top_k: int = 5) -> list[KBSearchResult]:
        hits = search_kb(query, top_k=top_k)
        return [
            KBSearchResult(
                article_id=h["metadata"].get("article_id"),
                title=h["metadata"].get("title", "Untitled"),
                snippet=(h["document"] or "")[:240],
                score=round(h["score"], 3),
            )
            for h in hits
        ]
