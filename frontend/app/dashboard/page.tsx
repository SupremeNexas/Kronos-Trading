'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getMarketOverview, getMarketTrending, getNewsFeed } from '@/lib/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Clock, Activity, Target, ShieldAlert, BarChart3, ArrowRight } from 'lucide-react';

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
      <div className="flex h-screen items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-red-400 p-6 text-center">
        <div>
          <ShieldAlert className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Connection Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const { indices = [], macro = {}, sectors = [] } = overview || {};
  const { gainers = [], losers = [], most_active = [] } = trending || {};

  // Formatter for numbers
  const formatNumber = (num: number) => num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 pb-20">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <header className="flex justify-between items-end border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-3xl font-bold">Market Dashboard</h1>
            <p className="text-slate-400 flex items-center gap-2 mt-1">
              <Clock size={14} /> Global Markets Overview
              <span className="bg-emerald-900/50 text-emerald-400 text-xs px-2 py-0.5 rounded border border-emerald-800 ml-2">LIVE</span>
            </p>
          </div>
          <Link href="/markets" className="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-1">
            Browse Markets <ArrowRight size={16} />
          </Link>
        </header>

        {/* Top KPIs (Indices) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {indices.slice(0, 4).map((idx: any) => {
            const isPos = idx.change >= 0;
            return (
              <div key={idx.symbol} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:bg-slate-800/50 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-slate-400 text-sm font-medium">{idx.name}</span>
                  <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300">{idx.symbol}</span>
                </div>
                <div>
                  <div className="text-2xl font-bold">{formatNumber(idx.price)}</div>
                  <div className={`flex items-center text-sm mt-1 font-medium ${isPos ? 'text-emerald-400' : 'text-red-400'}`}>
                    {isPos ? <TrendingUp size={16} className="mr-1" /> : <TrendingDown size={16} className="mr-1" />}
                    {isPos ? '+' : ''}{formatNumber(idx.change)} ({idx.change_pct}%)
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Middle Row: Macro & Sectors */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Sector Performance */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><BarChart3 size={18} className="text-blue-400"/> Sector Performance</h2>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={sectors} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="sector" type="category" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} width={120} />
                    <RechartsTooltip 
                      cursor={{fill: '#1e293b'}} 
                      contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px'}}
                      itemStyle={{color: '#34d399'}}
                      formatter={(val: any) => [`${val}%`, 'Performance']}
                    />
                    <Bar dataKey="performance_pct" radius={[0, 4, 4, 0]}>
                      {sectors.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.performance_pct >= 0 ? '#10b981' : '#ef4444'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Trending Tables */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="font-bold text-emerald-400 mb-4 flex items-center gap-2"><Target size={16}/> Top Gainers</h3>
                <div className="space-y-3">
                  {gainers.map((stock: any) => (
                    <Link href={`/stocks/${stock.symbol.toLowerCase()}`} key={stock.symbol} className="flex justify-between items-center group">
                      <div>
                        <div className="font-bold group-hover:text-emerald-400 transition-colors">{stock.symbol}</div>
                        <div className="text-xs text-slate-500">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{formatNumber(stock.price)}</div>
                        <div className="text-xs text-emerald-400">+{stock.change_pct}%</div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="font-bold text-red-400 mb-4 flex items-center gap-2"><Target size={16}/> Top Losers</h3>
                <div className="space-y-3">
                  {losers.map((stock: any) => (
                    <Link href={`/stocks/${stock.symbol.toLowerCase()}`} key={stock.symbol} className="flex justify-between items-center group">
                      <div>
                        <div className="font-bold group-hover:text-red-400 transition-colors">{stock.symbol}</div>
                        <div className="text-xs text-slate-500">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{formatNumber(stock.price)}</div>
                        <div className="text-xs text-red-400">{stock.change_pct}%</div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Macro & News */}
          <div className="space-y-6">
            
            {/* Macro Stats */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><Activity size={18} className="text-purple-400"/> Macro Environment</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-950 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Fed Rate</div>
                  <div className="font-bold">{macro.fed_funds_rate || 'N/A'}</div>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">10Y Yield</div>
                  <div className="font-bold">{macro.us_10y_yield || 'N/A'}</div>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">VIX Index</div>
                  <div className="font-bold">{macro.vix_volatility?.split(' ')[0] || 'N/A'}</div>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">DXY</div>
                  <div className="font-bold">{macro.dollar_index_dxy || 'N/A'}</div>
                </div>
              </div>
              <div className="mt-4 p-3 bg-slate-950 rounded-lg">
                <div className="flex justify-between items-center text-xs text-slate-500 mb-2">
                  <span>Sentiment Score</span>
                  <span>{macro.market_sentiment_label}</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-emerald-500" 
                    style={{ width: '100%' }}
                  >
                    <div className="relative w-full h-full">
                      <div className="absolute top-0 bottom-0 w-1 bg-white" style={{ left: `${macro.market_sentiment_score}%` }}></div>
                    </div>
                  </div>
                </div>
                <div className="text-center mt-1 text-sm font-bold">{macro.market_sentiment_score}/100</div>
              </div>
            </div>

            {/* News Feed */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-200">Market Intelligence</h2>
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {news.map((item: any) => {
                  let badgeColors = "bg-slate-800 text-slate-300";
                  if (item.sentiment === "BULLISH") badgeColors = "bg-emerald-900/30 text-emerald-400 border-emerald-800/50";
                  if (item.sentiment === "BEARISH") badgeColors = "bg-red-900/30 text-red-400 border-red-800/50";

                  return (
                    <div key={item.id} className="border-b border-slate-800/50 pb-4 last:border-0 last:pb-0">
                      <div className="flex justify-between items-start mb-1 gap-2">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${badgeColors}`}>
                          {item.sentiment}
                        </span>
                        <span className="text-xs text-slate-500 whitespace-nowrap">{item.time_ago}</span>
                      </div>
                      <h4 className="font-semibold text-sm leading-snug mb-1 hover:text-blue-400 cursor-pointer">{item.title}</h4>
                      <p className="text-xs text-slate-400 line-clamp-2">{item.summary}</p>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
