'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getMarketOverview, getMarketTrending, getNewsFeed } from '@/lib/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, Cell } from 'recharts';

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [trending, setTrending] = useState<any>(null);
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [overviewRes, trendingRes, newsRes] = await Promise.all([
          getMarketOverview(),
          getMarketTrending(),
          getNewsFeed()
        ]);
        setOverview(overviewRes.data);
        setTrending(trendingRes.data);
        setNews(newsRes.data.news || []);
      } catch (err: any) {
        console.error("Dashboard error:", err);
        setError("Failed to load dashboard data. Ensure backend is running.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--surface-canvas)]">
        <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[var(--color-smoke)] uppercase">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--surface-canvas)]">
        <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[#ff4a4a] uppercase border border-[#ff4a4a] px-4 py-2">
          {error}
        </div>
      </div>
    );
  }

  const { indices = [], macro = {}, sectors = [] } = overview || {};
  const { gainers = [], losers = [], most_active = [] } = trending || {};

  const formatNumber = (num: number) => num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[80px]">

        {/* MARKET OVERVIEW Section */}
        <section>
          {/* Section Eyebrow Bracket */}
          <div className="flex items-center justify-between mb-6">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
              [ MARKET OVERVIEW ]
            </div>
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
              B 01
            </div>
          </div>

          <h2 className="text-display-serif font-light text-[49px] leading-[1.05] tracking-[-1px] text-[var(--color-chalk)] mb-8">
            Pulse of the <span className="italic text-[var(--color-signal-lime)]">Market.</span>
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-[20px]">
            {/* INDEXES */}
            {indices.slice(0, 4).map((idx: any) => {
              const isPos = idx.change >= 0;
              return (
                <div key={idx.symbol} className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                  <div className="flex justify-between items-start mb-6">
                    <span className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">{idx.name}</span>
                  </div>
                  <div>
                    <div className="text-code-mono text-[20px] font-normal text-[var(--color-chalk)] leading-none mb-2">{formatNumber(idx.price)}</div>
                    <div className={`text-code-mono text-[11px] font-normal ${isPos ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-ash)]'}`}>
                      {isPos ? '+' : ''}{formatNumber(idx.change)} ({idx.change_pct}%)
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* MARKET BREADTH & TEMPERATURE */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-[20px]">
          {/* Trending (Watchlist proxy) */}
          <div className="lg:col-span-2 bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
              [ WATCHLIST ]
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-[40px]">
              {/* Gainers */}
              <div>
                <h3 className="text-display-serif text-[20px] text-[var(--color-chalk)] mb-4">Top Gainers</h3>
                <div className="space-y-[1px] bg-[var(--color-graphite)] border border-[var(--color-graphite)]">
                  {gainers.slice(0, 5).map((stock: any) => (
                    <Link href={`/stocks/${stock.symbol.toLowerCase()}`} key={stock.symbol} className="flex justify-between items-center bg-[var(--surface-card)] hover:bg-[var(--surface-hover)] p-3 group border-b border-[var(--color-graphite)] last:border-b-0">
                      <div>
                        <div className="text-ui-sans text-[13px] font-medium text-[var(--color-chalk)]">{stock.symbol}</div>
                        <div className="text-ui-sans text-[11px] text-[var(--color-ash)] truncate w-32">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-code-mono text-[13px] text-[var(--color-chalk)]">{formatNumber(stock.price)}</div>
                        <div className="text-code-mono text-[11px] text-[var(--color-signal-lime)]">+{stock.change_pct}%</div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>

              {/* Losers */}
              <div>
                <h3 className="text-display-serif text-[20px] text-[var(--color-chalk)] mb-4">Top Losers</h3>
                <div className="space-y-[1px] bg-[var(--color-graphite)] border border-[var(--color-graphite)]">
                  {losers.slice(0, 5).map((stock: any) => (
                    <Link href={`/stocks/${stock.symbol.toLowerCase()}`} key={stock.symbol} className="flex justify-between items-center bg-[var(--surface-card)] hover:bg-[var(--surface-hover)] p-3 group border-b border-[var(--color-graphite)] last:border-b-0">
                      <div>
                        <div className="text-ui-sans text-[13px] font-medium text-[var(--color-chalk)]">{stock.symbol}</div>
                        <div className="text-ui-sans text-[11px] text-[var(--color-ash)] truncate w-32">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-code-mono text-[13px] text-[var(--color-chalk)]">{formatNumber(stock.price)}</div>
                        <div className="text-code-mono text-[11px] text-[var(--color-ash)]">{stock.change_pct}%</div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Macro / Risk */}
          <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px] flex flex-col">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
              [ MACRO CONTEXT ]
            </div>

            <div className="flex-1 space-y-6">
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <span className="text-ui-sans text-[12px] text-[var(--color-smoke)]">FED RATE</span>
                <span className="text-code-mono text-[13px] text-[var(--color-chalk)]">{macro.fed_funds_rate || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <span className="text-ui-sans text-[12px] text-[var(--color-smoke)]">10Y YIELD</span>
                <span className="text-code-mono text-[13px] text-[var(--color-chalk)]">{macro.us_10y_yield || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <span className="text-ui-sans text-[12px] text-[var(--color-smoke)]">VIX INDEX</span>
                <span className="text-code-mono text-[13px] text-[var(--color-chalk)]">{macro.vix_volatility?.split(' ')[0] || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <span className="text-ui-sans text-[12px] text-[var(--color-smoke)]">DXY INDEX</span>
                <span className="text-code-mono text-[13px] text-[var(--color-chalk)]">{macro.dollar_index_dxy || 'N/A'}</span>
              </div>

              <div className="mt-8 pt-4">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2">SENTIMENT</div>
                <div className="text-display-serif text-[32px] text-[var(--color-chalk)]">
                  {macro.market_sentiment_score || '--'}<span className="text-[16px] text-[var(--color-ash)]">/100</span>
                </div>
                <div className="text-ui-sans text-[12px] text-[var(--color-signal-lime)] mt-1 uppercase tracking-[0.1em]">{macro.market_sentiment_label || 'NEUTRAL'}</div>
              </div>
            </div>
          </div>
        </section>

        {/* LEADING INDUSTRIES / CHART */}
        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ SECTOR PERFORMANCE ]
          </div>
          <div className="h-[300px] w-full mt-8">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectors} margin={{ top: 5, right: 0, left: -20, bottom: 5 }}>
                <YAxis type="number" stroke="var(--color-slate)" tick={{fill: 'var(--color-ash)', fontFamily: 'var(--font-jetbrains-mono)', fontSize: 10}} axisLine={false} tickLine={false} />
                <XAxis dataKey="sector" type="category" stroke="var(--color-graphite)" tick={{fill: 'var(--color-ash)', fontFamily: 'var(--font-inter-tight)', fontSize: 11}} axisLine={false} tickLine={false} />
                <RechartsTooltip
                  cursor={{fill: 'var(--surface-hover)'}}
                  contentStyle={{backgroundColor: 'var(--surface-raised)', borderColor: 'var(--color-slate)', color: 'var(--color-chalk)', borderRadius: '0px', fontFamily: 'var(--font-jetbrains-mono)', fontSize: '11px'}}
                  itemStyle={{color: 'var(--color-signal-lime)'}}
                  formatter={(val: any) => [`${val}%`, 'Alpha']}
                />
                <Bar dataKey="performance_pct" radius={[0, 0, 0, 0]}>
                  {sectors.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.performance_pct >= 0 ? 'var(--color-smoke)' : 'var(--color-fog)'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* MARKET INTELLIGENCE / RESEARCH */}
        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ MARKET INTELLIGENCE · 01 ]
          </div>
          <h2 className="text-display-serif text-[40px] leading-[1.05] text-[var(--color-chalk)] mb-8 max-w-2xl">
            Why is the market moving?
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-[40px]">
            {news.slice(0, 4).map((item: any) => (
              <div key={item.id} className="border-t border-[var(--color-graphite)] pt-6">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-ui-sans text-[10px] font-medium uppercase tracking-[0.18em] border border-[var(--color-slate)] px-2 py-1 text-[var(--color-smoke)]">
                    {item.sentiment}
                  </span>
                  <span className="text-code-mono text-[11px] text-[var(--color-ash)]">{item.time_ago}</span>
                </div>
                <h4 className="text-ui-sans text-[16px] font-normal leading-[1.4] text-[var(--color-chalk)] mb-2 hover:text-[var(--color-signal-lime)] cursor-pointer transition-colors max-w-md">
                  {item.title}
                </h4>
                <p className="text-ui-sans text-[14px] text-[var(--color-ash)] line-clamp-2 max-w-md">
                  {item.summary}
                </p>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}