from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plain password for registration")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., description="Tag name")


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    id: int

    class Config:
        from_attributes = True


# Recipe Schemas
class RecipeBase(BaseModel):
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = None
    instructions: Optional[str] = None


class RecipeCreate(RecipeBase):
    tag_ids: Optional[List[int]] = Field(default=None, description="List of tag IDs to associate")


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class RecipeOut(RecipeBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut] = []

    class Config:
        from_attributes = True


# Favorite Schemas
class FavoriteCreate(BaseModel):
    recipe_id: int


class FavoriteOut(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    created_at: datetime

    class Config:
        from_attributes = True
