"""
Portfolio Service - Core portfolio analysis logic
"""

from datetime import datetime
from app.models.holding import Holding
from app.models.portfolio import PortfolioAnalysis, RiskBreakdown
from app.models.common import Warning, Recommendation, BlindSpot
from app.services.market_data_service import get_market_data_service
from app.core.allocation import calculate_allocation
from app.core.scoring import calculate_risk_score


class PortfolioService:
    """
    Service for comprehensive portfolio analysis.
    """
    
    def __init__(self):
        self.market_data = get_market_data_service()
    
    async def analyze(self, holdings: list[Holding]) -> PortfolioAnalysis:
        """
        Perform comprehensive portfolio analysis.
        
        Args:
            holdings: List of portfolio holdings
            
        Returns:
            Complete portfolio analysis
        """
        # Fetch current prices
        symbols = [h.symbol for h in holdings]
        prices = await self.market_data.get_prices(symbols)
        
        # Use purchase price as fallback for missing prices
        for holding in holdings:
            if prices.get(holding.symbol) is None:
                prices[holding.symbol] = holding.purchase_price
        
        # Calculate total value and cost basis
        total_value = sum(
            h.quantity * prices.get(h.symbol, h.purchase_price)
            for h in holdings
        )
        
        total_cost_basis = sum(
            h.quantity * h.purchase_price
            for h in holdings
        )
        
        total_gain_loss = total_value - total_cost_basis
        total_gain_loss_pct = (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        # Calculate allocations
        asset_class_allocation, sector_allocation = calculate_allocation(holdings, prices)
        
        # Calculate risk score
        risk_score, risk_breakdown = calculate_risk_score(holdings, prices)
        
        # Generate warnings (imported from risk service logic)
        warnings = self._generate_warnings(holdings, prices, sector_allocation, asset_class_allocation)
        
        # Generate blind spots (imported from blind spot service logic)
        blind_spots = self._detect_blind_spots(holdings, sector_allocation)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            holdings, prices, sector_allocation, asset_class_allocation
        )
        
        return PortfolioAnalysis(
            total_value=round(total_value, 2),
            total_cost_basis=round(total_cost_basis, 2),
            total_gain_loss=round(total_gain_loss, 2),
            total_gain_loss_pct=round(total_gain_loss_pct, 2),
            allocation=asset_class_allocation,
            sector_allocation=sector_allocation,
            risk_score=risk_score,
            risk_breakdown=RiskBreakdown(**risk_breakdown),
            warnings=warnings,
            recommendations=recommendations,
            blind_spots=blind_spots,
            timestamp=datetime.utcnow(),
        )
    
    def _generate_warnings(
        self,
        holdings: list[Holding],
        prices: dict[str, float],
        sector_allocation: dict[str, float],
        asset_class_allocation: dict[str, float]
    ) -> list[Warning]:
        """Generate warnings based on concentration thresholds"""
        from app.models.common import WarningSeverity, WarningType
        
        warnings = []
        
        # Calculate total value
        total_value = sum(
            h.quantity * prices.get(h.symbol, h.purchase_price)
            for h in holdings
        )
        
        if total_value == 0:
            return warnings
        
        # Check sector concentration
        for sector, pct in sector_allocation.items():
            if pct > 40:
                affected = [
                    h.symbol for h in holdings
                    if self._get_sector(h.symbol, h.asset_class) == sector
                ]
                warnings.append(Warning(
                    type=WarningType.SECTOR_CONCENTRATION,
                    severity=WarningSeverity.CRITICAL,
                    message=f"Portfolio is {pct:.1f}% exposed to {sector} sector",
                    details={"sector": sector, "percentage": pct},
                    affected_symbols=affected,
                ))
            elif pct > 25:
                affected = [
                    h.symbol for h in holdings
                    if self._get_sector(h.symbol, h.asset_class) == sector
                ]
                warnings.append(Warning(
                    type=WarningType.SECTOR_CONCENTRATION,
                    severity=WarningSeverity.MEDIUM,
                    message=f"{sector} sector represents {pct:.1f}% of portfolio",
                    details={"sector": sector, "percentage": pct},
                    affected_symbols=affected,
                ))
        
        # Check single stock concentration
        for holding in holdings:
            value = holding.quantity * prices.get(holding.symbol, holding.purchase_price)
            pct = (value / total_value) * 100
            
            if pct > 20:
                warnings.append(Warning(
                    type=WarningType.SINGLE_STOCK,
                    severity=WarningSeverity.CRITICAL,
                    message=f"{holding.symbol} represents {pct:.1f}% of portfolio",
                    details={"symbol": holding.symbol, "percentage": pct},
                    affected_symbols=[holding.symbol],
                ))
            elif pct > 10:
                warnings.append(Warning(
                    type=WarningType.SINGLE_STOCK,
                    severity=WarningSeverity.MEDIUM,
                    message=f"{holding.symbol} represents {pct:.1f}% of portfolio",
                    details={"symbol": holding.symbol, "percentage": pct},
                    affected_symbols=[holding.symbol],
                ))
        
        # Check asset class imbalance
        for asset_class, pct in asset_class_allocation.items():
            if pct > 80:
                warnings.append(Warning(
                    type=WarningType.ASSET_CLASS_IMBALANCE,
                    severity=WarningSeverity.MEDIUM,
                    message=f"Portfolio is {pct:.1f}% {asset_class}",
                    details={"asset_class": asset_class, "percentage": pct},
                    affected_symbols=[],
                ))
        
        return warnings
    
    def _get_sector(self, symbol: str, asset_class: str) -> str:
        """Get sector for a symbol"""
        from app.core.allocation import get_sector
        sector = get_sector(symbol, asset_class)
        return sector or "Other"
    
    def _detect_blind_spots(
        self,
        holdings: list[Holding],
        sector_allocation: dict[str, float]
    ) -> list[BlindSpot]:
        """Detect blind spots using rules-based approach"""
        from app.models.common import BlindSpotType
        
        blind_spots = []
        
        # Rule 1: Style concentration (tech-heavy = large-cap growth proxy)
        tech_pct = sector_allocation.get('Technology', 0)
        if tech_pct > 60:
            affected = [
                h.symbol for h in holdings
                if self._get_sector(h.symbol, h.asset_class) == 'Technology'
            ]
            blind_spots.append(BlindSpot(
                type=BlindSpotType.STYLE_CONCENTRATION,
                confidence=min(95, 60 + int((tech_pct - 60) * 1.75)),
                message="Portfolio heavily tilted toward large-cap growth stocks",
                details={"dominant_style": "large_cap_growth", "percentage": tech_pct},
                affected_symbols=affected,
            ))
        
        # Rule 2: Hidden sector concentration (3+ holdings in same sector)
        sector_holdings = {}
        for h in holdings:
            sector = self._get_sector(h.symbol, h.asset_class)
            if sector not in sector_holdings:
                sector_holdings[sector] = []
            sector_holdings[sector].append(h.symbol)
        
        for sector, symbols in sector_holdings.items():
            if len(symbols) >= 3 and sector_allocation.get(sector, 0) > 40:
                blind_spots.append(BlindSpot(
                    type=BlindSpotType.HIDDEN_CORRELATION,
                    confidence=75,
                    message=f"High concentration in {sector} sector with {len(symbols)} holdings",
                    details={"sector": sector, "holding_count": len(symbols)},
                    affected_symbols=symbols,
                ))
        
        return blind_spots
    
    def _generate_recommendations(
        self,
        holdings: list[Holding],
        prices: dict[str, float],
        sector_allocation: dict[str, float],
        asset_class_allocation: dict[str, float]
    ) -> list[Recommendation]:
        """Generate rebalancing recommendations"""
        from app.models.common import RecommendationAction
        
        recommendations = []
        
        # Calculate total value
        total_value = sum(
            h.quantity * prices.get(h.symbol, h.purchase_price)
            for h in holdings
        )
        
        if total_value == 0:
            return recommendations
        
        # Find over-exposed sectors (>40%)
        for sector, pct in sector_allocation.items():
            if pct > 40:
                # Find largest holding in this sector
                sector_holdings = [
                    h for h in holdings
                    if self._get_sector(h.symbol, h.asset_class) == sector
                ]
                if sector_holdings:
                    largest = max(
                        sector_holdings,
                        key=lambda h: h.quantity * prices.get(h.symbol, h.purchase_price)
                    )
                    sell_qty = int(largest.quantity * 0.2)  # Suggest selling 20%
                    if sell_qty > 0:
                        recommendations.append(Recommendation(
                            action=RecommendationAction.SELL,
                            symbol=largest.symbol,
                            quantity=float(sell_qty),
                            reason=f"Reduce {sector} exposure from {pct:.1f}% to ~32%",
                            priority=1 if pct > 50 else 2,
                            expected_impact=f"Reduce risk score by {min(15, int((pct - 40) / 2))} points",
                        ))
        
        # Find over-exposed single stocks (>15%)
        for holding in holdings:
            value = holding.quantity * prices.get(holding.symbol, holding.purchase_price)
            pct = (value / total_value) * 100
            
            if pct > 15:
                sell_qty = int(holding.quantity * 0.3)  # Suggest selling 30%
                if sell_qty > 0:
                    recommendations.append(Recommendation(
                        action=RecommendationAction.SELL,
                        symbol=holding.symbol,
                        quantity=float(sell_qty),
                        reason=f"Reduce single-stock concentration from {pct:.1f}% to ~10%",
                        priority=1 if pct > 20 else 3,
                        expected_impact=f"Reduce risk score by {min(10, int((pct - 15) / 2))} points",
                    ))
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations
