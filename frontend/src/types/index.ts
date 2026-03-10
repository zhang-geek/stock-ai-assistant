export interface Quote {
  symbol: string;
  name: string;
  price: number;
  change_pct: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
  turnover?: number;
}

export interface DailyBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  change_pct: number;
  turnover?: number;
}

export interface IndexQuote {
  symbol: string;
  name: string;
  price: number;
  change_pct: number;
  amount: number;
}

export interface Sector {
  sector: string;
  code: string;
  price: number;
  change_pct: number;
  market_cap: number;
  turnover: number;
  up_count: number;
  down_count: number;
}

export interface Position {
  id: number;
  symbol: string;
  name: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  market_value: number;
  pnl: number;
  pnl_pct: number;
  entry_time: string;
}

export interface Portfolio {
  capital: number;
  cash: number;
  market_value: number;
  total_value: number;
  total_pnl: number;
  pnl_pct: number;
  positions: Position[];
}

export interface Transaction {
  id: number;
  strategy: string;
  symbol: string;
  action: 'buy' | 'sell';
  price: number;
  quantity: number;
  reasoning: string;
  timestamp: string;
}

export interface TradeStats {
  total_trades: number;
  paired_count: number;
  win_rate: number;
  avg_profit: number;
  max_profit: number;
  max_loss: number;
  profit_loss_ratio: number;
  most_traded: string;
  monthly_pnl: Record<string, number>;
}

export interface StyleData {
  avg_holding_days: number;
  trading_frequency: number;
  position_preference: string[];
  time_pattern: string;
  concentration: number;
  style_label: string;
  paired_count: number;
  total_trades: number;
}

export interface CostSummary {
  period_days: number;
  by_provider: Record<string, { calls: number; cost: number }>;
  by_task: Record<string, { calls: number; cost: number }>;
  total_cost_usd: number;
  total_calls: number;
}

export interface WatchlistItem {
  id: number;
  symbol: string;
  name: string;
  sector: string;
  notes: string;
  added_at: string;
}
