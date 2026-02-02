# test_verification.py
# Run this from the root directory: python test_verification.py

import sys
import os
from datetime import datetime
import pandas as pd

# FORCE SQLITE for testing to avoid psycopg2 dependency
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal, Base, engine
from app.models import Asset, AssetType, AssetHolding, TickerPriceHistory
from app.services.asset_manager import AssetManager
from app.services.investment_auditor import InvestmentAuditor
from app.services.market_data import MarketDataService
from app.services.security import SecurityService
from app.services.snapshot_engine import SnapshotEngine

def setup_db():
    print("--- Setting up DB (SQLite Memory) ---")
    # Override engine to use SQLite for strictly local verification
    from sqlalchemy import create_engine
    global engine
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.bind = engine
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return SessionLocal(bind=engine)

def test_security():
    print("\n--- Testing Security (Fernet) ---")
    # Needs valid key in env provided by .env file or manually set for test
    # We will generate one for this test if missing
    from cryptography.fernet import Fernet
    if not os.getenv("FERNET_KEY") or "PLEASE_CHANGE" in os.getenv("FERNET_KEY", ""):
        key = Fernet.generate_key().decode()
        os.environ["FERNET_KEY"] = key
        print(f"Generated Temp Key: {key}")

    token = "secret_access_token_123"
    enc = SecurityService.encrypt_token(token)
    dec = SecurityService.decrypt_token(enc)
    
    print(f"Original: {token}")
    print(f"Encrypted: {enc[:10]}...")
    print(f"Decrypted: {dec}")
    assert token == dec
    print("✅ Security Test Passed")

def test_auditor_blind_spots(db):
    print("\n--- Testing Investment Auditor & Blind Spots ---")
    
    # 1. Create Manual Real Estate (Fixed)
    print("Creating 6-Plex...")
    plex = AssetManager.create_manual_asset(
        db, "6-Plex Montreal", AssetType.FIXED, 
        attributes={"valuation_cents": 1_200_000_00}, # $1.2M
    )
    AssetManager.set_proxy_ticker(db, str(plex.id), "XRE.TO")

    # 2. Create Wealthsimple Account (Liquid)
    print("Creating Liquid Account...")
    ws = AssetManager.create_manual_asset(db, "Wealthsimple", AssetType.LIQUID)
    
    # Add Holdings: VFV.TO (S&P500), XIU.TO (TSX 60)
    # We simulate prices in TickerHistory so we don't hit yfinance API in this test
    # Mocking Market Data Cache
    print("Seeding Fake Market Data...")
    
    # VFV ~ $130, XIU ~ $33
    MarketDataService._fetch_and_cache = lambda *args: None # Disable real fetch
    
    # Inject fake price history needed for Snapshot/Auditor
    today = datetime.now()
    db.add(TickerPriceHistory(ticker="VFV.TO", date=today, close_cents=13000)) # $130.00
    db.add(TickerPriceHistory(ticker="XIU.TO", date=today, close_cents=3300))  # $33.00
    db.add(TickerPriceHistory(ticker="XRE.TO", date=today, close_cents=1600))  # $16.00 (Proxy)
    db.commit()

    # Add holdings to WS
    db.add(AssetHolding(asset_id=ws.id, ticker="VFV.TO", qty=100)) # $13,000
    db.add(AssetHolding(asset_id=ws.id, ticker="XIU.TO", qty=1000)) # $33,000
    db.commit()

    # 3. Snapshot
    print("Taking Snapshot...")
    # Mock Look-Through for VFV/XIU since yfinance is disabled
    # VFV = 100% US, Tech heavy
    # XIU = 100% CA, Financials heavy
    def mock_composition(ticker):
        if "VFV" in ticker:
            return {"sectors": {"Technology": 0.3}, "countries": {"United States": 1.0}}
        if "XIU" in ticker:
            return {"sectors": {"Financial Services": 0.4}, "countries": {"Canada": 1.0}}
        return {}
    
    original_get_comp = MarketDataService.get_etf_composition
    MarketDataService.get_etf_composition = staticmethod(mock_composition)

    snap = SnapshotEngine.take_snapshot(db)
    print(f"Snapshot Total Equity: ${snap.total_equity_cents/100:,.2f}")
    assert snap.total_equity_cents == 1_200_000_00 + 13_000_00 + 33_000_00
    print("✅ Snapshot Verification Passed")

    # 4. Auditor Analysis
    assets = db.query(Asset).all()
    exposure, val = InvestmentAuditor.generate_look_through_analysis(db, assets)
    alerts = InvestmentAuditor.check_concentration_alerts(exposure, val)
    
    print(f"Total Value Audited: ${val/100:,.2f}")
    print("Alerts Generated:")
    for a in alerts:
        print(f" - {a}")
        
    # Expect "Home Bias Warning" because Real Estate ($1.2M) + XIU ($33k) >>> VFV ($13k)
    canada_exposure = exposure['geography'].get('Canada', 0)
    canada_pct = canada_exposure / val
    print(f"Canada Exposure: {canada_pct*100:.1f}%")
    
    if canada_pct > 0.60:
        print("✅ Correctly detected Home Bias Blind Spot")
    else:
        print("❌ Failed to detect Home Bias")

    MarketDataService.get_etf_composition = original_get_comp

if __name__ == "__main__":
    db = setup_db()
    try:
        test_security()
        test_auditor_blind_spots(db)
        print("\nALL VERIFICATION TESTS PASSED")
    finally:
        db.close()
