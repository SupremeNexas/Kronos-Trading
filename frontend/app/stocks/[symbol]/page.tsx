'use client';

import { use } from 'react';
import { useEffect, useState } from 'react';
import { getMarketQuote, getMarketBars, getForecast } from '@/lib/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
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
      <div className="flex h-screen items-center justify-center bg-[var(--surface-canvas)]">
        <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[var(--color-smoke)] uppercase">Loading...</div>
      </div>
    );
  }

  if (error || !quote) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--surface-canvas)]">
        <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[#ff4a4a] uppercase border border-[#ff4a4a] px-4 py-2">
          {error || "No data returned for this symbol."}
        </div>
      </div>
    );
  }

  const isPos = quote.change >= 0;
  const ChartColor = isPos ? 'var(--color-smoke)' : 'var(--color-fog)';

  const formatNum = (num: number) => num?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00';

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[80px]">

        {/* Header - Quote */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
              [ STOCK ANALYSIS ]
            </div>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-start mb-8 gap-[40px]">
             <div>
                <h1 className="text-display-serif font-light text-[72px] leading-[0.98] tracking-[-1.8px] text-[var(--color-chalk)]">{upperSymbol}</h1>
                <div className="text-ui-sans text-[14px] text-[var(--color-smoke)] mt-2">{quote.name || "COMPANY INC."}</div>
             </div>
             <div className="flex flex-row items-end gap-[40px]">
                <div className="flex flex-col items-end">
                   <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)] mb-2">CURRENT PRICE</div>
                   <div className="text-code-mono text-[40px] text-[var(--color-chalk)] leading-none">${formatNum(quote.price)}</div>
                </div>
                <div className="flex flex-col items-end">
                   <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)] mb-2">DAY CHANGE</div>
                   <div className={`text-code-mono text-[20px] leading-none mb-1 ${isPos ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-ash)]'}`}>
                      {isPos ? '+' : ''}{formatNum(quote.change)} ({quote.change_pct}%)
                   </div>
                </div>
                <div className="flex flex-col items-end">
                   <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)] mb-2">VOLUME</div>
                   <div className="text-code-mono text-[20px] leading-none mb-1 text-[var(--color-chalk)]">
                      {quote.volume ? (quote.volume / 1000000).toFixed(2) + 'M' : '-'}
                   </div>
                </div>
             </div>
          </div>
        </section>

        {/* Main Chart */}
        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ PRICE ACTION ]
          </div>
          <div className="h-[400px] w-full">
            {bars.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={bars} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={ChartColor} stopOpacity={0.1}/>
                      <stop offset="95%" stopColor={ChartColor} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-graphite)" />
                  <XAxis dataKey="displayDate" tick={{fill: 'var(--color-ash)', fontFamily: 'var(--font-jetbrains-mono)', fontSize: 10}} axisLine={false} tickLine={false} minTickGap={30} />
                  <YAxis domain={['auto', 'auto']} tick={{fill: 'var(--color-ash)', fontFamily: 'var(--font-jetbrains-mono)', fontSize: 10}} axisLine={false} tickLine={false} orientation="right" />
                  <RechartsTooltip
                    contentStyle={{backgroundColor: 'var(--surface-raised)', borderColor: 'var(--color-slate)', color: 'var(--color-chalk)', borderRadius: '0px', fontFamily: 'var(--font-jetbrains-mono)', fontSize: '11px'}}
                    itemStyle={{color: 'var(--color-signal-lime)'}}
                    labelStyle={{color: 'var(--color-ash)', marginBottom: '4px', fontFamily: 'var(--font-inter-tight)'}}
                    formatter={(val: any) => [`$${val.toFixed(2)}`, 'Close']}
                  />
                  <Area type="monotone" dataKey="close" stroke={ChartColor} strokeWidth={1} fillOpacity={1} fill="url(#colorPrice)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-[var(--color-ash)] text-ui-sans text-[13px]">No chart data available.</div>
            )}
          </div>
        </section>

        {/* Forecast Section */}
        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="flex items-center justify-between mb-8">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
              [ KRONOS FORECAST ]
            </div>
            {forecast && (
               <div className="px-[10px] py-[4px] rounded-full border border-[var(--color-signal-lime)] text-[var(--color-signal-lime)] text-ui-sans text-[11px] tracking-[0.06em] font-medium">
                  ✓ MODEL ACTIVE
               </div>
            )}
          </div>

          {!forecast ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[var(--color-smoke)] uppercase">Running Models...</div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[40px]">

              {/* CURRENT */}
              <div className="border-t border-[var(--color-graphite)] pt-[24px]">
                 <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4">CURRENT</div>
                 <div className="text-code-mono text-[32px] text-[var(--color-chalk)] leading-none">${formatNum(forecast.current_price)}</div>
              </div>

              {/* TARGET */}
              <div className="border-t border-[var(--color-graphite)] pt-[24px]">
                 <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4">MODEL FORECAST</div>
                 <div className="text-code-mono text-[32px] text-[var(--color-chalk)] leading-none mb-2">${formatNum(forecast.target_price)}</div>
                 <div className={`text-code-mono text-[13px] ${forecast.expected_return_pct >= 0 ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-ash)]'}`}>
                    {forecast.expected_return_pct > 0 ? "+" : ""}{forecast.expected_return_pct.toFixed(2)}%
                 </div>
              </div>

              {/* HORIZON / CONFIDENCE */}
              <div className="border-t border-[var(--color-graphite)] pt-[24px]">
                 <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4">HORIZON</div>
                 <div className="text-code-mono text-[32px] text-[var(--color-chalk)] leading-none mb-4">{forecast.horizon_bars}D</div>
                 <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-1">CONFIDENCE</div>
                 <div className="text-code-mono text-[13px] text-[var(--color-chalk)]">{forecast.confidence_pct}%</div>
              </div>

              {/* SCENARIOS */}
              <div className="border-t border-[var(--color-graphite)] pt-[24px]">
                 <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4">ESTIMATED RANGE</div>
                 <div className="text-code-mono text-[16px] text-[var(--color-chalk)] mb-2">
                    ${formatNum(forecast.scenarios?.bear?.price)} — ${formatNum(forecast.scenarios?.bull?.price)}
                 </div>
                 <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mt-4 mb-2">CONSENSUS</div>
                 <div className={`text-ui-sans text-[11px] tracking-[0.1em] font-medium border px-2 py-1 inline-block ${
                      forecast.direction === 'BULLISH' ? 'border-[var(--color-signal-lime)] text-[var(--color-signal-lime)]' :
                      forecast.direction === 'BEARISH' ? 'border-[var(--color-ash)] text-[var(--color-chalk)]' :
                      'border-[var(--color-graphite)] text-[var(--color-smoke)]'
                    }`}>
                    {forecast.direction}
                 </div>
              </div>

            </div>
          )}
        </section>

      </div>
    </div>
  );
}