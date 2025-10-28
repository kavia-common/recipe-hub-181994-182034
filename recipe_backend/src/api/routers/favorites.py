from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from src.api.deps import get_db_session, get_current_user
from src.db import models, schemas

router = APIRouter(prefix="/", tags=["favorites"])


@router.post(
    "recipes/{recipe_id}/favorite",
    response_model=schemas.FavoriteOut,
    summary="Toggle favorite",
    description="Toggle favorite for the given recipe by the current user. Creates if not exists, otherwise removes and returns the previous favorite.",
)
def toggle_favorite(
    recipe_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """Toggle favorite for a recipe by current user."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    fav = (
        db.query(models.Favorite)
        .filter(models.Favorite.recipe_id == recipe_id, models.Favorite.user_id == current_user.id)
        .first()
    )
    if fav:
        # Unfavorite (delete) and return the deleted record (for convenience)
        db.delete(fav)
        db.commit()
        return fav
    new_fav = models.Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return new_fav


@router.get(
    "users/me/favorites",
    response_model=List[schemas.RecipeOut],
    summary="List my favorites",
    description="Return recipes that the current user has favorited.",
)
def list_my_favorites(
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """List recipes favorited by the authenticated user."""
    favorites = (
        db.query(models.Favorite)
        .options(selectinload(models.Favorite.recipe).selectinload(models.Recipe.tags))
        .filter(models.Favorite.user_id == current_user.id)
        .all()
    )
    recipes = [fav.recipe for fav in favorites if fav.recipe is not None]
    return recipes
