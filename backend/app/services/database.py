"""
Simple in-memory database for development.
Replace with PostgreSQL/Prisma in production.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import uuid

@dataclass
class User:
    id: str
    email: str
    passwordHash: Optional[str] = None  # Optional for OAuth users
    name: str = ""
    avatarUrl: Optional[str] = None
    emailVerified: Optional[datetime] = None
    createdAt: datetime = field(default_factory=datetime.utcnow)
    updatedAt: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Account:
    """OAuth account linked to User"""
    id: str
    userId: str
    provider: str  # 'google' or 'github'
    providerAccountId: str  # User's ID on the OAuth provider
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    expiresAt: Optional[datetime] = None
    scope: Optional[str] = None
    tokenType: Optional[str] = None
    idToken: Optional[str] = None
    createdAt: datetime = field(default_factory=datetime.utcnow)
    updatedAt: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Session:
    id: str
    userId: str
    token: str
    expiresAt: datetime
    createdAt: datetime = field(default_factory=datetime.utcnow)
    userAgent: Optional[str] = None
    ipAddress: Optional[str] = None

@dataclass
class Portfolio:
    id: str
    userId: str
    name: str
    description: Optional[str] = None
    isPublic: bool = False
    createdAt: datetime = field(default_factory=datetime.utcnow)
    updatedAt: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Holding:
    id: str
    portfolioId: str
    symbol: str
    quantity: float
    purchasePrice: float
    purchaseDate: Optional[datetime] = None
    assetClass: str = "stock"
    createdAt: datetime = field(default_factory=datetime.utcnow)
    updatedAt: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AuditLog:
    id: str
    userId: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None

class InMemoryDB:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.accounts: Dict[str, Account] = {}  # OAuth accounts
        self.sessions: Dict[str, Session] = {}
        self.portfolios: Dict[str, Portfolio] = {}
        self.holdings: Dict[str, Holding] = {}
        self.audit_logs: Dict[str, AuditLog] = {}
        self._lock = asyncio.Lock()
    
    async def user_find_by_email(self, email: str) -> Optional[User]:
        async with self._lock:
            for user in self.users.values():
                if user.email == email:
                    return user
            return None
    
    async def user_find_by_id(self, user_id: str) -> Optional[User]:
        async with self._lock:
            return self.users.get(user_id)
    
    async def user_create(self, email: str, passwordHash: str, name: str) -> User:
        async with self._lock:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                passwordHash=passwordHash,
                name=name
            )
            self.users[user.id] = user
            return user
    
    async def session_create(self, userId: str, token: str, expiresAt: datetime) -> Session:
        async with self._lock:
            session = Session(
                id=str(uuid.uuid4()),
                userId=userId,
                token=token,
                expiresAt=expiresAt
            )
            self.sessions[session.id] = session
            return session
    
    async def session_find_by_token(self, token: str) -> Optional[Session]:
        async with self._lock:
            for session in self.sessions.values():
                if session.token == token:
                    return session
            return None
    
    async def session_delete_many(self, userId: str):
        async with self._lock:
            to_delete = [k for k, v in self.sessions.items() if v.userId == userId]
            for k in to_delete:
                del self.sessions[k]
    
    async def portfolio_find_by_user(self, userId: str) -> Optional[Portfolio]:
        async with self._lock:
            for portfolio in self.portfolios.values():
                if portfolio.userId == userId:
                    return portfolio
            return None
    
    async def portfolio_create(self, userId: str, name: str, description: Optional[str] = None) -> Portfolio:
        async with self._lock:
            portfolio = Portfolio(
                id=str(uuid.uuid4()),
                userId=userId,
                name=name,
                description=description
            )
            self.portfolios[portfolio.id] = portfolio
            return portfolio
    
    async def holding_create(self, portfolioId: str, symbol: str, quantity: float, 
                            purchasePrice: float, assetClass: str = "stock") -> Holding:
        async with self._lock:
            holding = Holding(
                id=str(uuid.uuid4()),
                portfolioId=portfolioId,
                symbol=symbol.upper(),
                quantity=quantity,
                purchasePrice=purchasePrice,
                assetClass=assetClass
            )
            self.holdings[holding.id] = holding
            return holding
    
    async def holding_delete_by_portfolio(self, portfolioId: str):
        async with self._lock:
            to_delete = [k for k, v in self.holdings.items() if v.portfolioId == portfolioId]
            for k in to_delete:
                del self.holdings[k]
    
    async def holding_find_by_portfolio(self, portfolioId: str) -> List[Holding]:
        async with self._lock:
            return [h for h in self.holdings.values() if h.portfolioId == portfolioId]
    
    async def audit_log_create(
        self,
        userId: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ipAddress: Optional[str] = None,
        userAgent: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry"""
        async with self._lock:
            audit_log = AuditLog(
                id=str(uuid.uuid4()),
                userId=userId,
                action=action,
                details=details or {},
                ipAddress=ipAddress,
                userAgent=userAgent
            )
            self.audit_logs[audit_log.id] = audit_log
            return audit_log
    
    async def audit_log_find_by_user(self, userId: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a user"""
        async with self._lock:
            logs = [log for log in self.audit_logs.values() if log.userId == userId]
            logs.sort(key=lambda x: x.timestamp, reverse=True)
            return logs[:limit]
    
    async def account_find_by_provider_and_id(
        self, provider: str, providerAccountId: str
    ) -> Optional[Account]:
        """Find OAuth account by provider and provider's user ID"""
        async with self._lock:
            for account in self.accounts.values():
                if account.provider == provider and account.providerAccountId == providerAccountId:
                    return account
            return None
    
    async def account_find_by_user(self, userId: str) -> List[Account]:
        """Get all OAuth accounts linked to a user"""
        async with self._lock:
            return [a for a in self.accounts.values() if a.userId == userId]
    
    async def account_create(
        self,
        userId: str,
        provider: str,
        providerAccountId: str,
        accessToken: Optional[str] = None,
        refreshToken: Optional[str] = None,
        expiresAt: Optional[datetime] = None,
        scope: Optional[str] = None,
        tokenType: Optional[str] = None,
        idToken: Optional[str] = None,
    ) -> Account:
        """Create OAuth account linked to user"""
        async with self._lock:
            account = Account(
                id=str(uuid.uuid4()),
                userId=userId,
                provider=provider,
                providerAccountId=providerAccountId,
                accessToken=accessToken,
                refreshToken=refreshToken,
                expiresAt=expiresAt,
                scope=scope,
                tokenType=tokenType,
                idToken=idToken,
            )
            self.accounts[account.id] = account
            return account
    
    async def account_update_tokens(
        self,
        accountId: str,
        accessToken: Optional[str] = None,
        refreshToken: Optional[str] = None,
        expiresAt: Optional[datetime] = None,
    ) -> Optional[Account]:
        """Update OAuth account tokens"""
        async with self._lock:
            account = self.accounts.get(accountId)
            if not account:
                return None
            if accessToken is not None:
                account.accessToken = accessToken
            if refreshToken is not None:
                account.refreshToken = refreshToken
            if expiresAt is not None:
                account.expiresAt = expiresAt
            account.updatedAt = datetime.utcnow()
            return account

# Global database instance
db = InMemoryDB()

async def connect_db():
    """Connect to database (in-memory for now)"""
    print("✅ Database connected (in-memory mode)")

async def disconnect_db():
    """Disconnect from database"""
    print("🔌 Database disconnected")

async def get_db():
    """Get database connection"""
    yield db

def get_db_sync():
    """Get synchronous database connection"""
    return db
