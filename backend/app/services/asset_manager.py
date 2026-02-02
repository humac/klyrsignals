from sqlalchemy.orm import Session
from app.models import Asset, AssetType, ProviderType
from sqlalchemy.orm.attributes import flag_modified
from app.services.security import SecurityService
import uuid

class AssetManager:
    @staticmethod
    def create_manual_asset(db: Session, name: str, asset_type: AssetType, attributes: dict = None, access_token: str = None):
        """
        Creates a new manual asset (e.g. Real Estate Property).
        If access_token is provided (e.g. for Plaid later), it is encrypted.
        """
        if attributes is None:
            attributes = {}
        
        enc_token = None
        if access_token:
            enc_token = SecurityService.encrypt_token(access_token)
            
        asset = Asset(
            name=name,
            type=asset_type,
            provider_type=ProviderType.MANUAL,
            attributes=attributes,
            access_token_enc=enc_token
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def update_manual_valuation(db: Session, asset_id: str, valuation_cents: int):
        """
        Updates the manual valuation of an asset.
        """
        # Ensure UUID object
        if isinstance(asset_id, str):
            asset_id = uuid.UUID(asset_id)
            
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError("Asset not found")
            
        if asset.provider_type != ProviderType.MANUAL:
            raise ValueError("Cannot manually value a synced asset")

        # Update attributes
        asset.attributes['valuation_cents'] = valuation_cents
        flag_modified(asset, "attributes") # Notify SQLAlchemy of JSON update
        
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def set_proxy_ticker(db: Session, asset_id: str, proxy_ticker: str):
        """
        Sets a proxy ticker (e.g. XRE.TO) for a manual asset.
        """
        # Ensure UUID object
        if isinstance(asset_id, str):
            asset_id = uuid.UUID(asset_id)

        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError("Asset not found")
            
        asset.attributes['proxy_ticker'] = proxy_ticker
        flag_modified(asset, "attributes")
        
        db.commit()
        return asset
