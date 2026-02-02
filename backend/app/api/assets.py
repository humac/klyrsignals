from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Asset, AssetType
from app.services.asset_manager import AssetManager
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

router = APIRouter(prefix="/assets", tags=["Assets"])

# Pydantic Schemas
class AssetCreate(BaseModel):
    name: str
    type: str # Enum string
    attributes: Optional[Dict[str, Any]] = {}

class AssetUpdateValuation(BaseModel):
    valuation_cents: int

@router.get("/")
def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()

@router.post("/")
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    try:
        # Convert string to Enum
        # Simple validation
        try:
            atype = AssetType(asset.type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Asset Type")
            
        return AssetManager.create_manual_asset(
            db=db,
            name=asset.name,
            asset_type=atype,
            attributes=asset.attributes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{asset_id}/valuation")
def update_valuation(asset_id: str, val: AssetUpdateValuation, db: Session = Depends(get_db)):
    try:
        return AssetManager.update_manual_valuation(db, asset_id, val.valuation_cents)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
