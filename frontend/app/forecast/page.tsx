"use client";

import { useState } from "react";
import { Loader2, AlertTriangle, ArrowRight } from "lucide-react";
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

export default function ForecastStudio() {
  const [symbol, setSymbol] = useState("AAPL");
  const [interval, setInterval] = useState("1d");
  const [horizon, setHorizon] = useState(20);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any | null>(null);

  const fetchForecast = async () => {
    if (!symbol.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await getForecast(symbol.toUpperCase(), interval, horizon);
      setData(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.error || err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = data && data.ensemble_trajectory ? data.ensemble_trajectory.p50.map((p: number, i: number) => ({
      step: i + 1,
      p50: p,
      p10: data.ensemble_trajectory.p10[i],
      p90: data.ensemble_trajectory.p90[i],
      range: [data.ensemble_trajectory.p10[i], data.ensemble_trajectory.p90[i]]
  })) : [];

  return (
    <div className="min-h-screen bg-[var(--color-carbon)] text-[var(--color-bone)] font-sans p-6 md:p-8">
      <main className="max-w-[1280px] mx-auto space-y-12 pb-[120px]">
        
        {/* Header */}
        <section className="border-b border-[var(--color-graphite)] pb-8 mt-[80px]">
          <div className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-4">
            [ ASSET FORECAST ENGINE ]
          </div>
          <h1 className="font-serif font-light text-[40px] md:text-[56px] text-[var(--color-chalk)] tracking-[-1.5px] leading-[0.94] mb-2">
            See where the model sees the market going.
          </h1>
        </section>

        {/* Controls */}
        <div className="bg-[var(--color-onyx)] border border-[var(--color-graphite)] p-6 md:p-8 grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
          <div className="space-y-2">
            <label className="text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] block">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full bg-[var(--color-void-black)] border border-[var(--color-slate)] rounded-[4px] px-4 py-[10px] text-[14px] text-[var(--color-chalk)] focus:outline-none focus:border-[var(--color-signal-lime)] transition-colors uppercase"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] block">Timeframe</label>
            <select
              value={interval}
              onChange={(e) => setInterval(e.target.value)}
              className="w-full bg-[var(--color-void-black)] border border-[var(--color-slate)] rounded-[4px] px-4 py-[10px] text-[14px] text-[var(--color-chalk)] focus:outline-none focus:border-[var(--color-signal-lime)] transition-colors"
            >
              <option value="15m">15m</option>
              <option value="1h">1h</option>
              <option value="1d">1d</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] block">Horizon (Bars)</label>
            <select
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              className="w-full bg-[var(--color-void-black)] border border-[var(--color-slate)] rounded-[4px] px-4 py-[10px] text-[14px] text-[var(--color-chalk)] focus:outline-none focus:border-[var(--color-signal-lime)] transition-colors"
            >
              <option value="7">7 Bars</option>
              <option value="14">14 Bars</option>
              <option value="20">20 Bars</option>
              <option value="30">30 Bars</option>
            </select>
          </div>

          <button
              onClick={fetchForecast}
              disabled={loading || !symbol}
              className="h-[44px] bg-[var(--color-signal-lime)] text-[var(--color-void-black)] px-[32px] text-[14px] font-medium rounded-[4px] flex items-center justify-center gap-2 transition-transform active:scale-95 text-center shadow-[var(--shadow-sm)]"
              style={{boxShadow: 'var(--shadow-sm)'}}
            >
              {loading ? <Loader2 className="animate-spin w-4 h-4" /> : "RUN FORECAST"}
          </button>
        </div>

        {error && (
            <div className="border border-[#3d1818] bg-[#1a0a0a] p-6 flex flex-col items-center">
                <AlertTriangle className="text-red-500 mb-4" />
                <p className="text-[#e5e5e5]">{error}</p>
            </div>
        )}

        {/* Results */}
        {data && (
            <div className="space-y-12 animate-in fade-in duration-700">
                {/* Header Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="border hover:bg-[var(--color-iron)] transition-colors border-[var(--color-graphite)] bg-[var(--color-onyx)] p-6 rounded-none">
                        <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-4">{data.symbol}</p>
                        <p className="text-[32px] font-serif font-light text-[var(--color-chalk)] leading-none">${data.target_price?.toFixed(2)}</p>
                        <p className="text-[11px] text-[var(--color-ash)] mt-2">Target Price</p>
                    </div>

                    <div className="border hover:bg-[var(--color-iron)] transition-colors border-[var(--color-graphite)] bg-[var(--color-onyx)] p-6 rounded-none">
                        <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-4">Signal</p>
                        <p className={cn("text-[32px] font-serif font-light leading-none", data.direction === 'BULLISH' ? "text-[var(--color-signal-lime)]" : data.direction === 'BEARISH' ? "text-[#f43f5e]" : "text-[#fbbf24]")}>
                            {data.direction}
                        </p>
                    </div>
                    
                    <div className="border hover:bg-[var(--color-iron)] transition-colors border-[var(--color-graphite)] bg-[var(--color-onyx)] p-6 rounded-none">
                        <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-4">Exp Return</p>
                        <p className="text-[32px] font-serif font-light text-[var(--color-chalk)] leading-none">{data.expected_return > 0 ? "+" : ""}{data.expected_return?.toFixed(2)}%</p>
                    </div>

                    <div className="border hover:bg-[var(--color-iron)] transition-colors border-[var(--color-graphite)] bg-[var(--color-onyx)] p-6 rounded-none">
                        <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-4">Uncertainty</p>
                        <p className="text-[32px] font-serif font-light text-[var(--color-chalk)] leading-none">
                            {data.probability_distribution ? Math.abs((data.probability_distribution.p90 - data.probability_distribution.p10) / data.target_price * 100).toFixed(1) : "0"}%
                        </p>
                    </div>
                </div>
                
                {/* Chart Box */}
                <div className="border border-[var(--color-graphite)] bg-[var(--color-onyx)] p-6 rounded-none">
                    <div className="flex justify-between items-center mb-6">
                        <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase">[ FORECAST TRAJECTORY ]</p>
                        <div className="flex gap-4 items-center">
                            <span className="text-[11px] text-[var(--color-ash)] uppercase tracking-wide flex items-center gap-2"><div className="w-2 h-2 bg-[var(--color-signal-lime)]"></div> P50 BASE</span>
                            <span className="text-[11px] text-[var(--color-ash)] uppercase tracking-wide flex items-center gap-2"><div className="w-2 h-2 border border-[#314013] bg-[var(--color-olive-depth)]"></div> BAND</span>
                        </div>
                    </div>
                    <div className="h-[400px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#252525" vertical={false} />
                                <XAxis dataKey="step" stroke="#7a7a7a" tick={{fill: '#7a7a7a', fontSize: 11}} axisLine={false} tickLine={false} />
                                <YAxis stroke="#7a7a7a" domain={['auto', 'auto']} tickFormatter={(v)=>`$${v}`} tick={{fill: '#7a7a7a', fontSize: 11}} axisLine={false} tickLine={false} />
                                <Tooltip contentStyle={{backgroundColor: '#000000', border: '1px solid #3d3d3d', borderRadius: '4px'}} itemStyle={{color: '#ffffff', fontSize: '14px', fontFamily: 'monospace'}} />
                                <Area type="monotone" dataKey="range" stroke="none" fill="#314013" activeDot={false} fillOpacity={0.8} />
                                <Line type="monotone" dataKey="p50" stroke="#c5ff4a" strokeWidth={2} dot={false} activeDot={{r: 4, fill: '#c5ff4a', stroke: '#060606'}} />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Why Kronos Sees This */}
                    <div className="border border-[var(--color-graphite)] bg-[var(--color-onyx)] p-8">
                        <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-6">[ WHY KRONOS SEES THIS ]</p>
                        
                        <div className="space-y-8">
                            <div>
                                <h3 className="font-serif text-[24px] text-[var(--color-chalk)] mb-4">Supporting Signals</h3>
                                <ul className="space-y-3">
                                    {data.bullish_factors && data.bullish_factors.length > 0 ? data.bullish_factors.map((f: string, i: number) => (
                                        <li key={i} className="flex gap-3 text-[14px] text-[var(--color-bone)] leading-relaxed"><ArrowRight className="w-4 h-4 text-[var(--color-signal-lime)] flex-shrink-0 mt-1" /> {f}</li>
                                    )) : <li className="text-[14px] text-[var(--color-ash)]">No significant bullish factors isolated.</li>}
                                </ul>
                            </div>
                            
                            <div>
                                <h3 className="font-serif text-[24px] text-[var(--color-chalk)] mb-4">Opposing Signals</h3>
                                <ul className="space-y-3">
                                    {data.bearish_factors && data.bearish_factors.length > 0 ? data.bearish_factors.map((f: string, i: number) => (
                                        <li key={i} className="flex gap-3 text-[14px] text-[var(--color-bone)] leading-relaxed"><ArrowRight className="w-4 h-4 text-[#ef4444] flex-shrink-0 mt-1" /> {f}</li>
                                    )) : <li className="text-[14px] text-[var(--color-ash)]">No significant bearish factors isolated.</li>}
                                </ul>
                            </div>
                            
                            <div>
                                <h3 className="font-serif text-[24px] text-[var(--color-chalk)] mb-4">What Would Change The View</h3>
                                <ul className="space-y-3">
                                    {data.conditions_that_would_change_decision?.map((f: string, i: number) => (
                                        <li key={i} className="flex gap-3 text-[14px] text-[var(--color-bone)] leading-relaxed"><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-smoke)] flex-shrink-0 mt-2"></span> {f}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    {/* Model Stack */}
                    <div className="space-y-8 flex flex-col">
                        <div className="border border-[var(--color-graphite)] bg-[var(--color-onyx)] p-8 flex-1">
                            <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-6">[ MODEL STACK ]</p>
                            <div className="space-y-4">
                                {Object.entries(data.model_details || {}).map(([name, details]: any) => (
                                    <div key={name} className="flex justify-between items-center py-3 border-b border-[var(--color-iron)] last:border-0">
                                        <div className="text-[14px] text-[var(--color-bone)] uppercase font-medium">{name}</div>
                                        <div className={cn("text-[11px] px-3 py-1 uppercase tracking-wide border", details.status === "REAL" ? "text-[var(--color-signal-lime)] border-[var(--color-signal-lime)]" : (details.status === "UNAVAILABLE" ? "text-[var(--color-ash)] border-[var(--color-ash)]" : "text-[#eab308] border-[#eab308]"))}>
                                            {details.status}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                        
                        <div className="border border-[var(--color-graphite)] bg-[var(--color-void-black)] p-8">
                            <p className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-6">[ DATA PROVENANCE ]</p>
                            <div className="grid grid-cols-2 gap-y-4 text-[13px] font-mono">
                                <div><span className="text-[var(--color-smoke)]">Source:</span> Infoway M-D</div>
                                <div><span className="text-[var(--color-smoke)]">Model:</span> KRONOS-small</div>
                                <div><span className="text-[var(--color-smoke)]">Horiz:</span> {data.horizon} bars</div>
                                <div><span className="text-[var(--color-smoke)]">Gen:</span> {new Date(data.generated_at).toLocaleTimeString()}</div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        )}
      </main>
    </div>
  );
}
