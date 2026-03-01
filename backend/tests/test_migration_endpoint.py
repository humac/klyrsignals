"""
Test migration endpoint with sample data
"""
import asyncio
import sys
sys.path.insert(0, '/home/openclaw/.openclaw/workspace/jarvis/projects/klyrsignals/backend')

from app.services.database import db, connect_db
from app.services.auth import create_access_token
from datetime import timedelta

async def test_migration():
    """Test the migration flow"""
    print("🧪 Testing Migration Endpoint\n")
    
    # Connect to database
    await connect_db()
    
    # Create a test user
    print("1. Creating test user...")
    import hashlib
    # Use simple hash for testing (in production, use bcrypt)
    password_hash = hashlib.sha256("password123".encode()).hexdigest()
    user = await db.user_create(
        email="test@example.com",
        passwordHash=password_hash,
        name="Test User"
    )
    print(f"   ✅ User created: {user.id}")
    
    # Create access token
    print("\n2. Creating access token...")
    token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=15)
    )
    print(f"   ✅ Token created (truncated): {token[:50]}...")
    
    # Simulate localStorage portfolio data
    print("\n3. Preparing sample portfolio data...")
    sample_holdings = [
        {"symbol": "AAPL", "quantity": 50, "purchase_price": 150.00, "asset_class": "stock"},
        {"symbol": "MSFT", "quantity": 30, "purchase_price": 280.00, "asset_class": "stock"},
        {"symbol": "GOOGL", "quantity": 10, "purchase_price": 140.00, "asset_class": "stock"},
        {"symbol": "AAPL", "quantity": 25, "purchase_price": 160.00, "asset_class": "stock"},  # Duplicate
        {"symbol": "BTC", "quantity": 0.5, "purchase_price": 45000.00, "asset_class": "crypto"},
    ]
    print(f"   ✅ {len(sample_holdings)} holdings prepared (including 1 duplicate)")
    
    # Test migration endpoint
    print("\n4. Testing migration endpoint...")
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/api/v1/migrate/",
        json={
            "holdings": sample_holdings,
            "metadata": {
                "source": "localStorage",
                "test": True
            }
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Migration successful!")
        print(f"   - Portfolio ID: {result['portfolio_id']}")
        print(f"   - Holdings Migrated: {result['holdings_migrated']}")
        print(f"   - Holdings Failed: {result['holdings_failed']}")
        print(f"   - Message: {result['message']}")
        
        # Verify holdings were saved
        print("\n5. Verifying holdings in database...")
        portfolio = await db.portfolio_find_by_user(user.id)
        holdings = await db.holding_find_by_portfolio(portfolio.id)
        print(f"   ✅ Found {len(holdings)} holdings in database")
        
        for holding in holdings:
            print(f"   - {holding.symbol}: {holding.quantity} shares @ ${holding.purchasePrice}")
        
        # Verify audit log
        print("\n6. Verifying audit log...")
        audit_logs = await db.audit_log_find_by_user(user.id)
        migration_logs = [log for log in audit_logs if log.action == "portfolio_migration"]
        print(f"   ✅ Found {len(migration_logs)} migration audit log(s)")
        
        if migration_logs:
            log = migration_logs[0]
            print(f"   - Action: {log.action}")
            print(f"   - Details: {log.details}")
        
        print("\n✅ ALL TESTS PASSED")
        return True
    else:
        print(f"   ❌ Migration failed: {response.text}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_migration())
    sys.exit(0 if success else 1)
