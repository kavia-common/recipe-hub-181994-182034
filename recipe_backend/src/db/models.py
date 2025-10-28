from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Text,
    Table,
    Column,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

# Association table for many-to-many relationship between Recipe and Tag
recipe_tags_table: Table = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("recipe_id", "tag_id", name="uq_recipe_tag"),
)


class User(Base):
    """User model storing credentials and profile info."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe", back_populates="owner", cascade="all, delete-orphan"
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
    )


class Recipe(Base):
    """Recipe model containing main recipe details."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    instructions: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    owner: Mapped["User"] = relationship("User", back_populates="recipes")

    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=recipe_tags_table,
        back_populates="recipes",
        lazy="selectin",
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="recipe", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_recipes_title", "title"),
        Index("ix_recipes_owner_id", "owner_id"),
    )


class Tag(Base):
    """Tag model for categorizing recipes."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        secondary=recipe_tags_table,
        back_populates="tags",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_tags_name", "name"),
    )


class Favorite(Base):
    """Favorite model to track which users favorited which recipes."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_favorite"),
        Index("ix_favorites_user_id", "user_id"),
        Index("ix_favorites_recipe_id", "recipe_id"),
    )
