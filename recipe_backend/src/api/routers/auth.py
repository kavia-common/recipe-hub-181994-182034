from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db_session, get_current_user
from src.core.security import get_password_hash, verify_password, create_access_token
from src.db import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


@router.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account.",
)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db_session)) -> Any:
    """Create a new user with hashed password."""
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate user and return JWT.",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)) -> Any:
    """Authenticate user with email (as username) and password, then return JWT token."""
    # OAuth2PasswordRequestForm sends username field; we use it for email.
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    token = create_access_token(subject=user.id, expires_minutes=60)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=schemas.UserOut,
    summary="Get current user",
    description="Return the current authenticated user's profile.",
)
def read_me(current_user: models.User = Depends(get_current_user)) -> Any:
    """Return current authenticated user."""
    return current_user
