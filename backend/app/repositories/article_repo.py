"""Knowledge base article data access (relational metadata; vectors live in Chroma)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeArticle


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, article_id: int) -> KnowledgeArticle | None:
        return self.db.get(KnowledgeArticle, article_id)

    def add(self, article: KnowledgeArticle) -> KnowledgeArticle:
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def save(self, article: KnowledgeArticle) -> KnowledgeArticle:
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def delete(self, article: KnowledgeArticle) -> None:
        self.db.delete(article)
        self.db.commit()

    def list(self) -> list[KnowledgeArticle]:
        return list(self.db.scalars(select(KnowledgeArticle).order_by(KnowledgeArticle.title)))

    def increment_retrieval(self, article_id: int) -> None:
        article = self.get(article_id)
        if article:
            article.retrieval_count += 1
            self.db.add(article)
            self.db.commit()
