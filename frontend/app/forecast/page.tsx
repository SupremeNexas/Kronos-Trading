"use client";

import { useState } from "react";
import {
  Brain,
  TrendingUp,
  TrendingDown,
  Minus,
  Activity,
  ShieldAlert,
  Target,
  BarChart3,
  Loader2,
  AlertTriangle
} from "lucide-react";
import { getForecast } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Area,
  CartesianGrid
} from "recharts";

type Direction = "BULLISH" | "BEARISH" | "NEUTRAL";

interface ForecastData {
  symbol: string;
  current_price: number;
  horizon_bars: number;
  interval: string;
  direction: Direction;
  expected_return_pct: number;
  confidence_pct: number;
  model_agreement: string;
  model_agreement_pct: number;
  target_price: number;
  scenarios: {
    bull: { price: number; return_pct: number };
    base: { price: number; return_pct: number };
    bear: { price: number; return_pct: number };
  };
  probability_distribution: {
    p10: number; p25: number; p50: number; p75: number; p90: number;
  };
  ensemble_trajectory: {
    p50: number[];
    p10: number[];
    p90: number[];
  };
  overall_ai_score: number;
  models: Record<string, {
    model: string;
    direction: string;
    expected_return: number;
    confidence: number;
    trend_strength?: number;
  }>;
  finrl_strategy: { action: string; suggested_position_pct: number; risk_level: string };
  market_regime: { regime: string; volatility: string; trend: string };
  disclaimer: string;
}

export default function ForecastStudio() {
  const [symbol, setSymbol] = useState("AAPL");
  const [interval, setInterval] = useState("1d");
  const [horizon, setHorizon] = useState(20);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ForecastData | null>(null);

  const fetchForecast = async () => {
    if (!symbol.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await getForecast(symbol.toUpperCase(), interval, horizon);
      setData(response.data);
    } catch (err: any) {
      console.error("Failed to fetch forecast", err);
      setError(err?.response?.data?.error || err.message || "An unexpected error occurred while generating the forecast.");
    } finally {
      setLoading(false);
    }
  };

  const horizons = [7, 14, 20, 30, 60];
  const intervals = ["15m", "1h", "1d"];

  const buildChartData = () => {
    if (!data) return [];

    // Combining p10, p50, p90 into charting data points
    const { p10, p50, p90 } = data.ensemble_trajectory;
    const chartData = [];

    // Add current price as Day 0
    chartData.push({
      step: 0,
      p50: data.current_price,
      p10: data.current_price,
      p90: data.current_price,
      range: [data.current_price, data.current_price]
    });

    for (let i = 0; i < p50.length; i++) {
        chartData.push({
            step: i + 1,
            p50: p50[i],
            p10: p10[i],
            p90: p90[i],
            range: [p10[i], p90[i]]
        });
    }

    return chartData;
  };

  const chartData = buildChartData();

  const getDirectionColor = (dir: string) => {
    if (dir === "BULLISH") return "text-emerald-400";
    if (dir === "BEARISH") return "text-rose-400";
    return "text-amber-400";
  };

  const getDirectionBg = (dir: string) => {
    if (dir === "BULLISH") return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    if (dir === "BEARISH") return "bg-rose-500/10 text-rose-400 border-rose-500/20";
    return "bg-amber-500/10 text-amber-400 border-amber-500/20";
  };

  const getDirectionIcon = (dir: string) => {
    if (dir === "BULLISH") return <TrendingUp className="w-5 h-5 text-emerald-400" />;
    if (dir === "BEARISH") return <TrendingDown className="w-5 h-5 text-rose-400" />;
    return <Minus className="w-5 h-5 text-amber-400" />;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 md:p-8 space-y-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <header className="flex items-center gap-4 border-b border-slate-800 pb-6">
          <div className="p-3 bg-cyan-500/10 rounded-2xl border border-cyan-500/20">
            <Brain className="w-8 h-8 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-slate-50 to-slate-400 bg-clip-text text-transparent">
              AI Forecast Studio
            </h1>
            <p className="text-slate-400 mt-1">Multi-model ensemble price prediction & scenario analysis</p>
          </div>
        </header>

        {/* Controls */}
        <div className="fintech-card p-6 grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">Asset Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-50 focus:outline-none focus:border-cyan-500 transition-colors uppercase tabular-nums"
              placeholder="e.g. AAPL"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">Timeframe</label>
            <div className="flex bg-slate-900 border border-slate-700 rounded-lg overflow-hidden p-1">
              {intervals.map((int) => (
                <button
                  key={int}
                  onClick={() => setInterval(int)}
                  className={cn(
                    "flex-1 py-1.5 text-sm font-medium rounded-md transition-colors",
                    interval === int
                      ? "bg-slate-700 text-slate-50 shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  )}
                >
                  {int}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">Horizon (Bars)</label>
            <div className="flex bg-slate-900 border border-slate-700 rounded-lg overflow-hidden p-1">
              {horizons.map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className={cn(
                    "flex-1 py-1.5 text-sm font-medium rounded-md transition-colors tabular-nums",
                    horizon === h
                      ? "bg-slate-700 text-slate-50 shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  )}
                >
                  {h}
                </button>
              ))}
            </div>
          </div>

          <div>
            <button
              onClick={fetchForecast}
              disabled={loading || !symbol}
              className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Brain className="w-5 h-5" />}
              {loading ? "Analyzing..." : "Generate AI Forecast"}
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="fintech-card border-rose-500/30 bg-rose-500/5 p-6 flex flex-col items-center justify-center text-center space-y-4">
            <AlertTriangle className="w-12 h-12 text-rose-500" />
            <div>
              <h3 className="text-lg font-semibold text-rose-400">Analysis Failed</h3>
              <p className="text-slate-400 mt-1">{error}</p>
            </div>
            <button
              onClick={fetchForecast}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors text-sm font-medium"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && !data && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="fintech-card h-32 p-6 animate-pulse-subtle bg-slate-900/50" />
              ))}
            </div>
            <div className="fintech-card h-96 animate-pulse-subtle bg-slate-900/50" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="fintech-card h-64 animate-pulse-subtle bg-slate-900/50" />
              <div className="fintech-card h-64 animate-pulse-subtle bg-slate-900/50" />
            </div>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-panel rounded-xl p-6 flex flex-col justify-between">
                <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Consensus Direction</p>
                <div className="mt-4 flex items-center gap-4">
                  <div className={cn("p-4 rounded-full border", getDirectionBg(data.direction))}>
                    {getDirectionIcon(data.direction)}
                  </div>
                  <div>
                    <h2 className={cn("text-3xl font-bold", getDirectionColor(data.direction))}>
                      {data.direction}
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">Current: ${data.current_price.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              <div className="glass-panel rounded-xl p-6 flex flex-col justify-between">
                <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Expected Return</p>
                <div className="mt-4">
                  <h2 className={cn("text-4xl font-bold tabular-nums", data.expected_return_pct >= 0 ? "text-emerald-400" : "text-rose-400")}>
                    {data.expected_return_pct > 0 ? "+" : ""}{data.expected_return_pct.toFixed(2)}%
                  </h2>
                  <p className="text-slate-400 text-sm mt-1">Target: ${data.target_price.toFixed(2)}</p>
                </div>
              </div>

              <div className="glass-panel rounded-xl p-6 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Model Confidence</p>
                  <div className="px-2.5 py-1 rounded-md bg-slate-800 text-xs font-semibold text-slate-300">
                    {data.horizon_bars} {data.interval}
                  </div>
                </div>
                <div className="mt-4 flex items-end gap-3">
                  <h2 className="text-4xl font-bold tabular-nums text-slate-50">
                    {data.confidence_pct}%
                  </h2>
                  <p className="text-cyan-400 text-sm mb-1 font-medium">{data.model_agreement}</p>
                </div>
              </div>
            </div>

            {/* Main Chart */}
            <div className="glass-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-slate-50 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-cyan-400" />
                    Probabilistic Projection
                  </h3>
                  <p className="text-sm text-slate-400">P10 to P90 Confidence Interval ({data.horizon_bars} intervals)</p>
                </div>
                <div className="flex items-center gap-4 text-xs font-medium">
                  <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-sm bg-cyan-400"></div> P50 (Base)</div>
                  <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-sm bg-emerald-500/20 border border-emerald-500"></div> Bull / Bear Range</div>
                </div>
              </div>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="rangeGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.2}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis
                      dataKey="step"
                      stroke="#475569"
                      tick={{ fill: '#475569', fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      stroke="#475569"
                      tick={{ fill: '#475569', fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                      domain={['auto', 'auto']}
                      tickFormatter={(val) => `$${val}`}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '0.5rem', color: '#f8fafc' }}
                      itemStyle={{ color: '#cbd5e1' }}
                      formatter={(value: any, name: string) => {
                        if (name === "range") return null;
                        return [`$${Number(value).toFixed(2)}`, name.toUpperCase()];
                      }}
                      labelFormatter={(label) => `Step ${label}`}
                    />
                    <Area
                      type="monotone"
                      dataKey="range"
                      stroke="none"
                      fill="url(#rangeGradient)"
                      activeDot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="p50"
                      stroke="#22d3ee"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 6, fill: '#22d3ee', stroke: '#020617', strokeWidth: 2 }}
                    />
                    <Line type="monotone" dataKey="p90" stroke="#10b981" strokeWidth={1} strokeDasharray="4 4" dot={false} />
                    <Line type="monotone" dataKey="p10" stroke="#f43f5e" strokeWidth={1} strokeDasharray="4 4" dot={false} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* Scenarios */}
              <div className="fintech-card p-6 lg:col-span-1 space-y-4">
                <h3 className="text-lg font-semibold text-slate-50 flex items-center gap-2 mb-4">
                  <Target className="w-5 h-5 text-cyan-400" />
                  Scenario Analysis
                </h3>

                <div className="border border-emerald-500/20 bg-emerald-500/5 rounded-lg p-4 flex justify-between items-center relative overflow-hidden">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500"></div>
                  <div>
                    <p className="text-sm text-emerald-400 font-medium">Bull Case (P90)</p>
                    <p className="text-2xl font-bold text-slate-50 mt-1 tabular-nums">${data.scenarios.bull.price.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-emerald-400 font-bold tabular-nums">+{data.scenarios.bull.return_pct.toFixed(2)}%</p>
                  </div>
                </div>

                <div className="border border-cyan-500/20 bg-cyan-500/5 rounded-lg p-4 flex justify-between items-center relative overflow-hidden">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-cyan-500"></div>
                  <div>
                    <p className="text-sm text-cyan-400 font-medium">Base Case (P50)</p>
                    <p className="text-2xl font-bold text-slate-50 mt-1 tabular-nums">${data.scenarios.base.price.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className={cn("font-bold tabular-nums", data.scenarios.base.return_pct >= 0 ? "text-cyan-400" : "text-rose-400")}>
                      {data.scenarios.base.return_pct > 0 ? "+" : ""}{data.scenarios.base.return_pct.toFixed(2)}%
                    </p>
                  </div>
                </div>

                <div className="border border-rose-500/20 bg-rose-500/5 rounded-lg p-4 flex justify-between items-center relative overflow-hidden">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-rose-500"></div>
                  <div>
                    <p className="text-sm text-rose-400 font-medium">Bear Case (P10)</p>
                    <p className="text-2xl font-bold text-slate-50 mt-1 tabular-nums">${data.scenarios.bear.price.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-rose-400 font-bold tabular-nums">{data.scenarios.bear.return_pct.toFixed(2)}%</p>
                  </div>
                </div>
              </div>

              {/* Models Grid */}
              <div className="fintech-card p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold text-slate-50 flex items-center gap-2 mb-6">
                  <Activity className="w-5 h-5 text-cyan-400" />
                  Ensemble Models
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(data.models).map(([key, model]) => (
                    <div key={key} className="bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-colors">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-semibold text-slate-200">{model.model}</h4>
                        <span className={cn(
                           "text-xs px-2 py-0.5 rounded-full font-medium border",
                           getDirectionBg(model.direction)
                        )}>
                          {model.direction}
                        </span>
                      </div>
                      <div className="space-y-2 mt-4">
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-slate-400">Exp. Return</span>
                          <span className={cn("font-medium tabular-nums", model.expected_return >= 0 ? "text-emerald-400" : "text-rose-400")}>
                            {model.expected_return > 0 ? "+" : ""}{model.expected_return.toFixed(2)}%
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-slate-400">Confidence</span>
                          <span className="font-medium text-slate-200 tabular-nums">
                            {(model.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        {model.trend_strength && (
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-slate-400">Trend Score</span>
                            <span className="font-medium text-slate-200 tabular-nums">
                              {model.trend_strength}/100
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-6 border-t border-slate-800 grid grid-cols-2 gap-4">
                   <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800 flex items-center justify-between">
                      <div>
                        <p className="text-xs text-slate-400 uppercase font-medium">FinRL Strategy</p>
                        <p className="text-lg font-bold text-slate-50 mt-1">{data.finrl_strategy.action}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-slate-400">Position Size</p>
                        <p className="text-cyan-400 font-medium">{data.finrl_strategy.suggested_position_pct}%</p>
                      </div>
                   </div>
                   <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800 flex items-center justify-between">
                      <div>
                        <p className="text-xs text-slate-400 uppercase font-medium">Market Regime</p>
                        <p className="text-sm font-semibold text-slate-200 mt-1">{data.market_regime.regime}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-slate-400">Trend / Vol</p>
                        <p className="text-slate-300 text-sm font-medium">{data.market_regime.trend}</p>
                      </div>
                   </div>
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="border border-amber-500/30 bg-amber-500/10 rounded-xl p-4 flex items-start gap-4 mt-8">
              <ShieldAlert className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-amber-500">Forecasting Disclaimer</h4>
                <p className="text-xs text-amber-200/70 mt-1 leading-relaxed">
                  {data.disclaimer || "Model Forecast -- For analytical purposes only. Machine learning predictions are probabilistic and do not guarantee future performance. Market conditions can change rapidly. Always perform your own research."}
                </p>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}