from typing import Any, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, selectinload

from src.api.deps import get_db_session, get_current_user
from src.db import models, schemas

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _apply_filters(
    query,
    q: Optional[str],
    tag_ids: Optional[List[int]],
    cuisine: Optional[str],
):
    # For now, cuisine filtering could be modeled via tags named by cuisine, or skip if not present.
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(func.lower(models.Recipe.title).like(like) | func.lower(models.Recipe.description).like(like))
    if tag_ids:
        # Ensure recipe has all specified tags
        for tag_id in tag_ids:
            query = query.filter(models.Recipe.tags.any(models.Tag.id == tag_id))
    # Cuisine not modeled explicitly; attempt to map to tag by name if provided
    if cuisine:
        query = query.filter(models.Recipe.tags.any(func.lower(models.Tag.name) == cuisine.lower()))
    return query


def _sort_query(query, sort: Optional[str]):
    if sort == "title_asc":
        return query.order_by(asc(models.Recipe.title))
    if sort == "title_desc":
        return query.order_by(desc(models.Recipe.title))
    if sort == "newest":
        return query.order_by(desc(models.Recipe.created_at))
    if sort == "oldest":
        return query.order_by(asc(models.Recipe.created_at))
    return query.order_by(desc(models.Recipe.created_at))


def _paginate(query, page: int, page_size: int) -> Tuple[List[models.Recipe], int]:
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


@router.get(
    "",
    response_model=List[schemas.RecipeOut],
    summary="List recipes",
    description="List recipes with optional search, tag filter, cuisine filter, sorting, and pagination.",
)
def list_recipes(
    q: Optional[str] = Query(None, description="Search text"),
    tags: Optional[List[int]] = Query(None, description="Tag IDs to filter by"),
    cuisine: Optional[str] = Query(None, description="Cuisine filter (mapped to tag name if present)"),
    sort: Optional[str] = Query("newest", description="Sort order: newest|oldest|title_asc|title_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> Any:
    """Return a paginated recipe list applying filters and sorting."""
    base_q = db.query(models.Recipe).options(selectinload(models.Recipe.tags))
    base_q = _apply_filters(base_q, q, tags, cuisine)
    base_q = _sort_query(base_q, sort)
    items, _ = _paginate(base_q, page, page_size)
    return items


@router.get(
    "/{recipe_id}",
    response_model=schemas.RecipeOut,
    summary="Get recipe by ID",
    description="Retrieve a single recipe by its identifier.",
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db_session)) -> Any:
    """Get a single recipe by ID."""
    recipe = (
        db.query(models.Recipe)
        .options(selectinload(models.Recipe.tags))
        .filter(models.Recipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


def _set_recipe_tags(db: Session, recipe: models.Recipe, tag_ids: Optional[List[int]]) -> None:
    if tag_ids is None:
        return
    tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all() if tag_ids else []
    recipe.tags = tags


@router.post(
    "",
    response_model=schemas.RecipeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create recipe",
    description="Create a new recipe. Requires authentication.",
)
def create_recipe(
    recipe_in: schemas.RecipeCreate,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """Create a recipe and optionally associate tags."""
    recipe = models.Recipe(
        title=recipe_in.title,
        description=recipe_in.description,
        instructions=recipe_in.instructions,
        owner_id=current_user.id,
    )
    db.add(recipe)
    db.flush()  # assign ID for association
    _set_recipe_tags(db, recipe, recipe_in.tag_ids)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.put(
    "/{recipe_id}",
    response_model=schemas.RecipeOut,
    summary="Update recipe",
    description="Update a recipe. Only the author can update.",
)
def update_recipe(
    recipe_id: int,
    recipe_in: schemas.RecipeUpdate,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """Update recipe fields and tags if provided; author-only."""
    recipe = db.query(models.Recipe).options(selectinload(models.Recipe.tags)).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")

    if recipe_in.title is not None:
        recipe.title = recipe_in.title
    if recipe_in.description is not None:
        recipe.description = recipe_in.description
    if recipe_in.instructions is not None:
        recipe.instructions = recipe_in.instructions
    if recipe_in.tag_ids is not None:
        _set_recipe_tags(db, recipe, recipe_in.tag_ids)

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recipe",
    description="Delete a recipe. Only the author can delete.",
)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """Delete a recipe; author-only."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")
    db.delete(recipe)
    db.commit()
    return None
