"""F3: gap diagnosis, a ranked list of fixes with estimated impact."""

from fastapi import APIRouter

from app.api.deps import not_built
from app.models import Fix

router = APIRouter(prefix="/api", tags=["diagnosis"])


@router.get("/fixes")
def list_fixes() -> list[Fix]:
    """Store-wide fixes, highest estimated impact first."""
    not_built("04")


@router.get("/products/{product_id}/fixes")
def list_product_fixes(product_id: str) -> list[Fix]:
    not_built("04")
