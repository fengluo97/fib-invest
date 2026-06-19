export interface SymbolInfo {
  code: string;
  name: string;
  market: string;
}

export interface DailyBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  adj_factor: number;
}

export interface Signal {
  strategy_id: string;
  symbol: string;
  direction: "BUY" | "SELL" | "HOLD";
  strength: number;
  reason: string;
}

export interface Order {
  id: string;
  strategy_id: string;
  symbol: string;
  direction: "BUY" | "SELL";
  quantity: number;
  price: number;
  status: "pending" | "ready" | "submitted" | "partial_filled" | "filled" | "cancelled";
  filled_quantity: number;
  created_at: string;
}

export interface DashboardSummary {
  account: { total_value: number; cash: number; currency: string };
  positions: PositionInfo[];
  daily_pnl: number;
  strategies_running: number;
}

export interface PositionInfo {
  symbol: string;
  name: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface BacktestMetrics {
  total_return: number;
  annualized_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  win_rate: number;
  total_trades: number;
  total_pnl: number;
  final_equity: number;
}
