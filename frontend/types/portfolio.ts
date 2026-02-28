/**
 * Portfolio type definitions
 */

export interface Holding {
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date?: string;
  asset_class?: 'stock' | 'etf' | 'crypto' | 'mutual_fund';
}

export interface Warning {
  type: 'sector_concentration' | 'single_stock' | 'asset_class_imbalance' | 'geographic_concentration';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  details: Record<string, any>;
  affected_symbols: string[];
}

export interface Recommendation {
  action: 'buy' | 'sell' | 'hold';
  symbol: string;
  quantity?: number;
  reason: string;
  priority: number;
  expected_impact: string;
}

export interface BlindSpot {
  type: 'hidden_correlation' | 'style_concentration' | 'geographic_concentration' | 'market_cap_concentration';
  confidence: number;
  message: string;
  details: Record<string, any>;
  affected_symbols: string[];
}

export interface RiskBreakdown {
  concentration: number;
  volatility: number;
  correlation: number;
}

export interface PortfolioAnalysis {
  total_value: number;
  total_cost_basis: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
  allocation: Record<string, number>;
  sector_allocation: Record<string, number>;
  risk_score: number;
  risk_breakdown: RiskBreakdown;
  warnings: Warning[];
  recommendations: Recommendation[];
  blind_spots: BlindSpot[];
  timestamp: string;
}
