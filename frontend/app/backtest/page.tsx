'use client';

import React, { useState } from 'react';
import { runBacktest } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
  BarChart3,
  Settings2,
  Play,
  Loader2,
  AlertTriangle,
  Info,
  CheckCircle2,
  XCircle,
  TrendingUp,
  Activity,
  Target,
  RefreshCw,
  Gauge
} from 'lucide-react';

interface BacktestResult {
  symbol: string;
  walk_forward_windows_evaluated: number;
  mae_pct: number;
  naive_baseline_mae_pct: number;
  rmse_pct: number;
  mape_pct: number;
  directional_accuracy_pct: number;
  hit_rate_pct: number;
  interval_calibration_pct: number;
  benchmark_comparison: string;
}

export default function BacktestPage() {
  const [symbol, setSymbol] = useState("AAPL");
  const [horizon, setHorizon] = useState<number>(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const horizons = [7, 10, 14, 20, 30];

  const handleRunBacktest = async () => {
    if (!symbol.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await runBacktest(symbol.toUpperCase(), "1d", horizon);
      if (response && response.success && response.backtest) {
        setResult(response.backtest);
      } else {
        setError("Failed to run backtest. Invalid response format.");
      }
    } catch (err: any) {
      setError(err?.message || "An unexpected error occurred during backtesting.");
    } finally {
      setLoading(false);
    }
  };

  const isImprovement = result ? result.mae_pct < result.naive_baseline_mae_pct : false;
  const maeImprovement = result ? (result.naive_baseline_mae_pct - result.mae_pct).toFixed(2) : "0.00";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 md:p-10 font-sans flex justify-center">
      <div className="w-full max-w-6xl space-y-8">

        {/* Header */}
        <header className="flex items-center space-x-4 mb-8">
          <div className="p-3 bg-slate-900 rounded-xl border border-slate-800">
            <BarChart3 className="w-8 h-8 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-1">
              Walk-Forward Backtesting Engine
            </h1>
            <p className="text-slate-400 text-sm">
              Rigorous out-of-sample model validation across rolling time windows.
            </p>
          </div>
        </header>

        {/* Controls Section */}
        <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <div className="flex flex-col md:flex-row gap-6 items-end">
            <div className="flex-1 w-full space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center space-x-2">
                <Settings2 className="w-4 h-4 text-slate-400" />
                <span>Asset Symbol</span>
              </label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="e.g. AAPL"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all uppercase"
                disabled={loading}
              />
            </div>

            <div className="flex-1 w-full space-y-2">
              <label className="text-sm font-medium text-slate-300">Forecast Horizon (Days)</label>
              <div className="flex bg-slate-950 border border-slate-800 rounded-lg p-1">
                {horizons.map((h) => (
                  <button
                    key={h}
                    onClick={() => setHorizon(h)}
                    disabled={loading}
                    className={cn(
                      "flex-1 py-1.5 text-sm font-medium rounded-md transition-all",
                      horizon === h
                        ? "bg-slate-800 text-cyan-400 shadow-sm"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
                    )}
                  >
                    {h}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleRunBacktest}
              disabled={loading || !symbol.trim()}
              className="w-full md:w-auto px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-lg shadow-lg shadow-cyan-900/20 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 min-w-[200px]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  <span>Run Walk-Forward</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-rose-950/30 border border-rose-900/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-4 animate-in fade-in">
            <div className="p-3 bg-rose-900/20 rounded-full">
              <AlertTriangle className="w-8 h-8 text-rose-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-rose-200">Execution Failed</h3>
              <p className="text-rose-400/80 text-sm mt-1">{error}</p>
            </div>
            <button
              onClick={handleRunBacktest}
              className="px-4 py-2 bg-rose-900/40 hover:bg-rose-900/60 text-rose-200 text-sm font-medium rounded-lg transition-colors flex items-center space-x-2 mt-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Analysis</span>
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="fintech-card bg-slate-900/50 border border-slate-800/50 rounded-xl p-6 flex flex-col justify-between h-36 animate-pulse">
                <div className="w-24 h-5 bg-slate-800 rounded-md"></div>
                <div className="w-20 h-10 bg-slate-800 rounded-md mt-4"></div>
                <div className="w-32 h-4 bg-slate-800 rounded-md mt-2"></div>
              </div>
            ))}
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6 animate-in fade-in duration-500">
            {/* Main Benchmark Badge */}
            <div className={cn(
              "w-full p-4 rounded-xl border flex items-center justify-center space-x-3 shadow-lg",
              isImprovement
                ? "bg-emerald-950/20 border-emerald-900/50 shadow-emerald-900/10"
                : "bg-rose-950/20 border-rose-900/50 shadow-rose-900/10"
            )}>
              {isImprovement ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-rose-400 flex-shrink-0" />
              )}
              <h2 className={cn(
                "text-lg font-semibold",
                isImprovement ? "text-emerald-300" : "text-rose-300"
              )}>
                {result.benchmark_comparison}
              </h2>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

              {/* MAE */}
              <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-slate-400 font-medium text-sm flex items-center gap-1.5">
                    <Target className="w-4 h-4 text-cyan-500" />
                    MAE %
                  </h3>
                  <div className="group-hover:opacity-100 opacity-0 transition-opacity" title="Mean Absolute Error across windows">
                    <Info className="w-4 h-4 text-slate-500" />
                  </div>
                </div>
                <div className="text-3xl font-bold tabular-nums text-white my-1">
                  {result.mae_pct.toFixed(2)}%
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Mean Absolute Error (Lower is better)
                </p>
              </div>

              {/* Baseline MAE */}
              <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-slate-400 font-medium text-sm flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-slate-500" />
                    Baseline MAE %
                  </h3>
                </div>
                <div className="text-3xl font-bold tabular-nums text-slate-300 my-1">
                  {result.naive_baseline_mae_pct.toFixed(2)}%
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Naive persistent model baseline
                </p>
              </div>

              {/* MAE Improvement */}
              <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-slate-400 font-medium text-sm flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-emerald-500" />
                    MAE Imprv. vs Baseline
                  </h3>
                </div>
                <div className="text-3xl font-bold tabular-nums my-1 flex items-center gap-2">
                  <span className={isImprovement ? "text-emerald-400" : "text-rose-400"}>
                    {isImprovement ? '+' : ''}{maeImprovement}%
                  </span>
                  {isImprovement && (
                    <span className="px-2 py-0.5 bg-emerald-950/50 text-emerald-400 text-[10px] uppercase font-bold tracking-wider rounded-md border border-emerald-900/50">
                      Beat Baseline
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Difference relative to baseline MAE
                </p>
              </div>

              {/* RMSE */}
              <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-slate-400 font-medium text-sm flex items-center gap-1.5">
                    <Target className="w-4 h-4 text-blue-500" />
                    RMSE %
                  </h3>
                </div>
                <div className="text-3xl font-bold tabular-nums text-white my-1">
                  {result.rmse_pct.toFixed(2)}%
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Root Mean Square Error
                </p>
              </div>

              {/* Directional Accuracy */}
              <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-slate-400 font-medium text-sm flex items-center gap-1.5">
                    <Gauge className="w-4 h-4 text-purple-500" />
                    Directional Acc & Hit Rate
                  </h3>
                </div>
                <div className="flex items-end gap-2 mt-1">
                  <div className="text-3xl font-bold tabular-nums text-white">
                    {result.hit_rate_pct.toFixed(1)}%
                  </div>
                  <div className="text-sm font-medium text-slate-400 mb-1">
                    / {result.directional_accuracy_pct.toFixed(1)}%
                  </div>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Correct trend prediction percentage
                </p>
              </div>

              {/* Windows & Calibration */}
              <div className="fintech-card bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-slate-400 font-medium text-sm flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-orange-500" />
                    Walk-Forward Windows
                  </h3>
                </div>
                <div className="flex items-end gap-3 mt-1">
                  <div className="text-3xl font-bold tabular-nums text-white">
                    {result.walk_forward_windows_evaluated}
                  </div>
                  <div className="text-sm font-medium text-emerald-400 mb-1 flex items-center gap-1">
                    {result.interval_calibration_pct.toFixed(1)}% cal.
                  </div>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Evaluation windows & interval calibration
                </p>
              </div>
            </div>

            {/* Explanation Section */}
            <div className="mt-8 pt-6 border-t border-slate-800/80">
              <h3 className="text-lg font-medium text-slate-200 mb-4 flex items-center gap-2">
                <Info className="w-5 h-5 text-cyan-500" />
                Model Validation Metrics Explained
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5 text-sm text-slate-400">
                <div className="space-y-1">
                  <span className="font-semibold text-slate-300 block">MAE (Mean Absolute Error)</span>
                  <p>Average absolute prediction error across all walk-forward windows. Measures the typical magnitude of price forecast misses.</p>
                </div>
                <div className="space-y-1">
                  <span className="font-semibold text-slate-300 block">RMSE (Root Mean Square Error)</span>
                  <p>Root mean square error -- penalizes larger deviations more heavily than MAE, highlighting when the model makes significant out-of-bounds mistakes.</p>
                </div>
                <div className="space-y-1">
                  <span className="font-semibold text-slate-300 block">Hit Rate / Directional Accuracy</span>
                  <p>Percentage of windows where the predicted direction exactly matched the actual price movement direction over the forecast horizon.</p>
                </div>
                <div className="space-y-1">
                  <span className="font-semibold text-slate-300 block">Walk-Forward Windows</span>
                  <p>Number of non-overlapping evaluation windows tested systematically throughout the historical data for an unbiased out-of-sample gauge.</p>
                </div>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
