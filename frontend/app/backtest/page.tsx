'use client';

import React, { useState } from 'react';
import { runBacktest } from '@/lib/api';

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
      if (response && response.data?.success && response.data?.backtest) {
        setResult(response.data?.backtest);
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
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[40px]">

        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ OUT-OF-SAMPLE VALIDATION ]
          </div>
          
          <h2 className="text-display-serif font-light text-[49px] leading-[1.05] tracking-[-1px] text-[var(--color-chalk)] mb-12">
            Walk-Forward <span className="italic text-[var(--color-signal-lime)]">Engine.</span>
          </h2>

          <div className="flex flex-col md:flex-row gap-[16px] items-end justify-between border-b border-[var(--color-graphite)] pb-8 mb-8">
            <div className="flex flex-col gap-2 w-full max-w-xs">
              <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">
                ASSET SYMBOL
              </label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="AAPL..."
                className="bg-transparent border border-[var(--color-slate)] p-2 text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none uppercase"
                disabled={loading}
              />
            </div>

            <div className="flex flex-col gap-2 w-full max-w-xs">
              <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">
                FORECAST HORIZON
              </label>
              <div className="flex bg-[var(--surface-raised)] border border-[var(--color-graphite)] h-[42px]">
                {horizons.map((h) => (
                  <button
                    key={h}
                    onClick={() => setHorizon(h)}
                    disabled={loading}
                    className={`flex-1 text-code-mono text-[13px] transition-colors border-r border-[var(--color-graphite)] last:border-r-0 ${
                      horizon === h
                        ? "bg-[var(--color-signal-lime)] text-[var(--color-void-black)]"
                        : "text-[var(--color-smoke)] hover:text-[var(--color-chalk)] bg-transparent"
                    }`}
                  >
                    {h}D
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleRunBacktest}
              disabled={loading || !symbol.trim()}
              className="px-[32px] h-[44px] bg-[var(--color-signal-lime)] text-[var(--color-void-black)] text-ui-sans text-[13px] font-medium tracking-[0.08em] uppercase transition-transform active:scale-95 glow-signal disabled:opacity-50"
            >
              {loading ? 'PROCESSING...' : 'RUN WALK-FORWARD'}
            </button>
          </div>

          {error && (
            <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[#ff4a4a] uppercase border border-[#ff4a4a] px-4 py-2 mb-8">
              {error}
            </div>
          )}

          {result && !loading && (
            <div className="space-y-[40px]">
              <div className="bg-[var(--surface-raised)] border border-[var(--color-graphite)] p-[24px] flex items-center justify-between">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">BENCHMARK COMPARISON</div>
                <div className={`text-code-mono text-[16px] font-normal ${isImprovement ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                  {result.benchmark_comparison}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[20px]">
                {/* MAE */}
                <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">MAE %</div>
                  <div>
                    <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none mb-1">
                      {result.mae_pct.toFixed(2)}%
                    </div>
                    <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">Mean Absolute Error</div>
                  </div>
                </div>

                {/* Baseline MAE */}
                <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">BASELINE MAE %</div>
                  <div>
                    <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none mb-1">
                      {result.naive_baseline_mae_pct.toFixed(2)}%
                    </div>
                    <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">Naive persistent model</div>
                  </div>
                </div>

                {/* MAE Improvement */}
                <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">IMPROVEMENT</div>
                  <div>
                    <div className={`text-code-mono text-[32px] font-normal leading-none mb-1 ${isImprovement ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                      {isImprovement ? '+' : ''}{maeImprovement}%
                    </div>
                    <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">Vs. baseline MAE</div>
                  </div>
                </div>

                {/* RMSE */}
                <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">RMSE %</div>
                  <div>
                    <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none mb-1">
                      {result.rmse_pct.toFixed(2)}%
                    </div>
                    <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">Root Mean Square Error</div>
                  </div>
                </div>

                {/* Directional Accuracy */}
                <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">ACCURACY</div>
                  <div>
                    <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none mb-1">
                      {result.directional_accuracy_pct.toFixed(1)}%
                    </div>
                    <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">Directional hit rate: {result.hit_rate_pct.toFixed(1)}%</div>
                  </div>
                </div>

                {/* Windows */}
                <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">EVAL WINDOWS</div>
                  <div>
                    <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none mb-1">
                      {result.walk_forward_windows_evaluated}
                    </div>
                    <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">Cal: {result.interval_calibration_pct.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
