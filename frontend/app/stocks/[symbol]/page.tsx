'use client';

import { use } from 'react';
import { useEffect, useState } from 'react';
import { getMarketQuote, getMarketBars, getForecast } from '@/lib/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { TrendingUp, TrendingDown, Activity, AlertTriangle, ShieldCheck, Target, BarChart2 } from 'lucide-react';
import { format, parseISO } from 'date-fns';

export default function StockAnalysisPage({ params }: { params: Promise<{ symbol: string }> }) {
  const { symbol } = use(params);
  const upperSymbol = symbol.toUpperCase();

  const [quote, setQuote] = useState<any>(null);
  const [bars, setBars] = useState<any[]>([]);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        // Load quote and bars for initial render
        const [quoteRes, barsRes] = await Promise.all([
          getMarketQuote(upperSymbol),
          getMarketBars(upperSymbol, '1d', 90)
        ]);
        setQuote(quoteRes.data);
        
        let processedBars = [];
        if (barsRes.data.bars && barsRes.data.bars.length > 0) {
          processedBars = barsRes.data.bars.map((b: any) => ({
            ...b,
            displayDate: format(parseISO(b.timestamp), 'MMM dd')
          }));
        }
        setBars(processedBars);

        // Fire off forecast but don't block render
        getForecast(upperSymbol, '1d', 20).then(res => {
          setForecast(res.data);
        }).catch(err => {
          console.error("Forecast error:", err);
        });

      } catch (err: any) {
        console.error("Stock load error:", err);
        setError("Failed to load generic data for " + upperSymbol);
      } finally {
        setLoading(false);
      }
    }
    if (upperSymbol) {
      loadData();
    }
  }, [upperSymbol]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (error || !quote) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-red-400 p-6">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Error</h2>
          <p>{error || "No data returned for this symbol."}</p>
        </div>
      </div>
    );
  }

  const isPos = quote.change >= 0;
  const priceColor = isPos ? 'text-emerald-400' : 'text-red-400';
  const ChartColor = isPos ? '#10b981' : '#ef4444';

  const formatNum = (num: number) => num?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 pb-20">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header - Quote */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-xl">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-extrabold">{upperSymbol}</h1>
              <span className={`px-2 py-1 text-xs font-bold rounded ${quote.data_status === 'SIMULATED' ? 'bg-amber-900/40 text-amber-500 border border-amber-800' : 'bg-emerald-900/40 text-emerald-500 border border-emerald-800'}`}>
                {quote.data_status || 'DELAYED'}
              </span>
            </div>
            <div className="flex items-end gap-4 mt-2">
              <span className="text-5xl font-mono tracking-tight">${formatNum(quote.price)}</span>
              <div className={`flex items-center text-xl font-medium pb-1 ${priceColor}`}>
                {isPos ? <TrendingUp size={24} className="mr-1" /> : <TrendingDown size={24} className="mr-1" />}
                {isPos ? '+' : ''}{formatNum(quote.change)} ({quote.change_pct}%)
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 md:mt-0 w-full md:w-auto p-4 bg-slate-950 rounded-xl border border-slate-800">
            <div>
              <div className="text-slate-500 text-xs mb-1">Vol</div>
              <div className="font-semibold">{quote.volume ? (quote.volume / 1000000).toFixed(2) + 'M' : '-'}</div>
            </div>
            <div>
              <div className="text-slate-500 text-xs mb-1">Open</div>
              <div className="font-semibold">{formatNum(quote.open)}</div>
            </div>
            <div>
              <div className="text-slate-500 text-xs mb-1">High</div>
              <div className="font-semibold">{formatNum(quote.high)}</div>
            </div>
            <div>
              <div className="text-slate-500 text-xs mb-1">Low</div>
              <div className="font-semibold">{formatNum(quote.low)}</div>
            </div>
          </div>
        </div>

        {/* Main Chart */}
        <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-lg">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2"><BarChart2 className="text-blue-400"/> Price Action (90 Days)</h2>
          <div className="h-80 w-full">
            {bars.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={bars} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={ChartColor} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={ChartColor} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                  <XAxis dataKey="displayDate" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} minTickGap={30} />
                  <YAxis domain={['auto', 'auto']} tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} orientation="right" />
                  <RechartsTooltip 
                    contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px'}}
                    itemStyle={{color: ChartColor}}
                    labelStyle={{color: '#94a3b8', marginBottom: '4px'}}
                    formatter={(val: number) => [`$${val.toFixed(2)}`, 'Close']}
                  />
                  <Area type="monotone" dataKey="close" stroke={ChartColor} strokeWidth={2} fillOpacity={1} fill="url(#colorPrice)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-slate-500">No chart data available.</div>
            )}
          </div>
        </div>

        {/* Forecast Section */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-950 p-6 rounded-2xl border border-slate-800 shadow-lg relative overflow-hidden">
          {/* Subtle bg glow */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Activity className="text-purple-400" /> AI Ensemble Forecast
            </h2>
            <div className="flex items-center gap-2 mt-2 md:mt-0 px-3 py-1 bg-slate-800 rounded-full border border-slate-700 text-xs text-slate-300">
              <ShieldCheck size={14} className="text-blue-400"/>
              Model Forecast — Not Financial Advice
            </div>
          </div>

          {!forecast ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Activity className="w-10 h-10 text-emerald-500 animate-pulse mb-4" />
              <p className="text-slate-400 animate-pulse">Running Ensemble Models (TimesFM + Chronos-2)...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Target Tile */}
              <div className="col-span-1 bg-slate-900 border border-slate-700/50 p-6 rounded-xl flex flex-col justify-between">
                <div>
                  <div className="text-sm text-slate-400 mb-1 font-medium">{forecast.horizon_bars} {forecast.interval} Target</div>
                  <div className="text-4xl font-bold tracking-tight">${forecast.target_price}</div>
                  <div className={`mt-2 font-bold ${forecast.expected_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    Exp Return: {forecast.expected_return_pct}%
                  </div>
                </div>
                
                <div className="mt-6">
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>Confidence Score</span>
                    <span className="font-bold text-white">{forecast.confidence_pct}/100</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500" style={{ width: `${forecast.confidence_pct}%` }} />
                  </div>
                  <div className="mt-4 flex items-center gap-2">
                    <div className={`px-4 py-2 flex-grow text-center rounded-lg font-bold text-white shadow-lg ${
                      forecast.direction === 'BULLISH' ? 'bg-gradient-to-r from-emerald-600 to-emerald-400' :
                      forecast.direction === 'BEARISH' ? 'bg-gradient-to-r from-red-600 to-red-400' :
                      'bg-gradient-to-r from-slate-600 to-slate-400'
                    }`}>
                      {forecast.direction}
                    </div>
                  </div>
                </div>
              </div>

              {/* Scenarios Tile */}
              <div className="col-span-1 bg-slate-900 border border-slate-700/50 p-6 rounded-xl">
                <h3 className="font-bold mb-4 flex items-center gap-2"><Target size={18}/> Price Scenarios</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-emerald-400 font-bold">Bull (P90)</span>
                      <span>${forecast.scenarios?.bull?.price}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full"><div className="h-full bg-emerald-500 rounded-full" style={{width: '90%'}}></div></div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-blue-400 font-bold">Base (P50)</span>
                      <span>${forecast.scenarios?.base?.price}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full"><div className="h-full bg-blue-500 rounded-full" style={{width: '50%'}}></div></div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-red-400 font-bold">Bear (P10)</span>
                      <span>${forecast.scenarios?.bear?.price}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full"><div className="h-full bg-red-500 rounded-full" style={{width: '10%'}}></div></div>
                  </div>
                </div>
                <div className="mt-6 pt-4 border-t border-slate-800 text-sm">
                  <span className="text-slate-400">Model Agreement:</span> <span className="font-semibold">{forecast.model_agreement}</span>
                </div>
              </div>

              {/* Technicals Tile */}
              <div className="col-span-1 bg-slate-900 border border-slate-700/50 p-6 rounded-xl">
                <h3 className="font-bold mb-4">Technical & Strategy</h3>
                <div className="space-y-3 font-mono text-xs">
                  <div className="flex justify-between p-2 bg-slate-950 rounded">
                    <span className="text-slate-400">Trend</span>
                    <span className={forecast.models?.technical?.trend === 'UP' ? 'text-emerald-400' : 'text-red-400'}>
                      {forecast.models?.technical?.trend || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between p-2 bg-slate-950 rounded">
                    <span className="text-slate-400">RSI (14)</span>
                    <span className={forecast.models?.technical?.rsi > 70 ? 'text-red-400' : forecast.models?.technical?.rsi < 30 ? 'text-emerald-400' : 'text-slate-200'}>
                      {forecast.models?.technical?.rsi ? forecast.models?.technical?.rsi.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between p-2 bg-slate-950 rounded">
                    <span className="text-slate-400">MACD</span>
                    <span className={(forecast.models?.technical?.macd || 0) > 0 ? 'text-emerald-400' : 'text-red-400'}>
                      {forecast.models?.technical?.macd ? forecast.models?.technical?.macd.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between p-2 bg-slate-950 rounded">
                    <span className="text-slate-400">Regime</span>
                    <span className="text-blue-400">{forecast.market_regime?.volatility || 'MODERATE'} VOL</span>
                  </div>
                  <div className="flex justify-between p-2 bg-slate-950 rounded border border-emerald-900 mt-2">
                    <span className="text-slate-400">FinRL Action</span>
                    <span className="font-bold text-white">{forecast.finrl_strategy?.action || 'HOLD'}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="mt-6 text-center text-xs text-slate-500 border-t border-slate-800 pt-4">
            AI-generated model forecasts are for analytical research only. Past performance does not guarantee future results.
          </div>
        </div>

      </div>
    </div>
  );
}
