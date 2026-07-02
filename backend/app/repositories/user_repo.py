"""User & Role data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role, User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_agents(self, department: str) -> list[User]:
        from app.core.security import Role as R

        stmt = select(User).where(
            User.role_name.in_(tuple(R.AGENT_ROLES)),
            User.department == department,
        )
        return list(self.db.scalars(stmt))

    def pick_available_agent(self, department: str) -> User | None:
        """Least-loaded available agent in a department (simple round-robin-ish)."""
        agents = [a for a in self.list_agents(department) if a.is_available]
        if not agents:
            agents = self.list_agents(department)
        return agents[0] if agents else None


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, name: str, description: str = "") -> Role:
        role = self.db.scalar(select(Role).where(Role.name == name))
        if role is None:
            role = Role(name=name, description=description)
            self.db.add(role)
            self.db.commit()
        return role

    def list(self) -> list[Role]:
        return list(self.db.scalars(select(Role)))
