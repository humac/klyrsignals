from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Asset
from app.services.investment_auditor import InvestmentAuditor

router = APIRouter(prefix="/auditor", tags=["Auditor"])

@router.get("/look-through")
def get_look_through_analysis(db: Session = Depends(get_db)):
    """
    Returns the sector and geographic breakdown of the portfolio.
    """
    # In a real scenario, this might take a snapshot_id
    # asking for "Current" state
    assets = db.query(Asset).all()
    exposure, total_val = InvestmentAuditor.generate_look_through_analysis(db, assets)
    
    return {
        "total_value_cents": total_val,
        "exposure": exposure
    }

@router.get("/alerts")
def get_concentration_alerts(db: Session = Depends(get_db)):
    """
    Returns a list of warnings if the portfolio violates concentration thresholds.
    """
    assets = db.query(Asset).all()
    exposure, total_val = InvestmentAuditor.generate_look_through_analysis(db, assets)
    
    alerts = InvestmentAuditor.check_concentration_alerts(exposure, total_val)
    return {"alerts": alerts}

@router.get("/correlation_matrix")
def get_correlation_matrix(db: Session = Depends(get_db)):
    """
    Returns the correlation matrix JSON.
    """
    assets = db.query(Asset).all()
    df = InvestmentAuditor.calculate_correlation_matrix(db, assets)
    # Convert DF to JSON compatible format (e.g. dict of dicts)
    # df.to_json() returns a string, we want an object
    return df.to_dict()
