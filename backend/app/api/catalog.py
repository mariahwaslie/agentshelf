"""F1: catalog import and PayPal Catalog Products sync."""

from fastapi import APIRouter, UploadFile

from app.api.deps import not_built
from app.models import ImportResult, Product, SyncResult

router = APIRouter(prefix="/api", tags=["catalog"])


@router.post("/catalog/import")
def import_catalog(file: UploadFile | None = None) -> ImportResult:
    """Load the seed catalog, or an uploaded CSV/JSON file (≤ 2 MB, ≤ 1,000 rows). Idempotent."""
    not_built("03")


@router.post("/catalog/sync")
def sync_catalog() -> SyncResult:
    """Create or update every product in the PayPal sandbox catalog and store its PayPal ID."""
    not_built("03")


@router.get("/products")
def list_products() -> list[Product]:
    not_built("03")


@router.get("/products/{product_id}")
def get_product(product_id: str) -> Product:
    not_built("03")
