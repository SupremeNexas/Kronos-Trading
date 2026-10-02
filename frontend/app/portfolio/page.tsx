'use client';

import React, { useState, useEffect } from 'react';
import { getPortfolio, getTradingAccount, getTradingPositions } from '@/lib/api';

const formatCurrency = (val: number | undefined | null) => {
  if (val === undefined || val === null) return '$0.00';
  return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatPercent = (val: number | undefined | null) => {
  if (val === undefined || val === null) return '0.00%';
  return (val > 0 ? '+' : '') + val.toFixed(2) + '%';
};

export default function PortfolioPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [account, setAccount] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [accRes, posRes, portRes] = await Promise.all([
        getTradingAccount(),
        getTradingPositions(),
        getPortfolio()
      ]);
      setAccount(accRes.data || accRes);
      const positionsData = posRes.data?.positions || posRes.data || [];
      setPositions(Array.isArray(positionsData) ? positionsData : []);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch portfolio data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
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

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[80px]">

        {/* PORTFOLIO SUMMARY */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
              [ PORTFOLIO SUMMARY ]
            </div>
            <button onClick={fetchData} className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] hover:text-[var(--color-chalk)]">
               REFRESH
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[20px]">
             {/* PORTFOLIO VALUE */}
             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">PORTFOLIO VALUE</div>
                <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none">{formatCurrency(account?.total_equity)}</div>
             </div>

             {/* DAY P&L */}
             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">DAY P&L</div>
                <div>
                   <div className={`text-code-mono text-[32px] font-normal leading-none mb-1 ${account?.today_pnl >= 0 ? "text-[var(--color-signal-lime)]" : "text-[var(--color-ash)]"}`}>
                      {account?.today_pnl >= 0 ? '+' : ''}{formatCurrency(account?.today_pnl)}
                   </div>
                   <div className={`text-code-mono text-[11px] ${account?.today_pnl_pct >= 0 ? "text-[var(--color-signal-lime)]" : "text-[var(--color-ash)]"}`}>
                      {formatPercent(account?.today_pnl_pct)}
                   </div>
                </div>
             </div>

             {/* TOTAL P&L */}
             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">TOTAL P&L</div>
                <div>
                   <div className={`text-code-mono text-[32px] font-normal leading-none mb-1 ${account?.unrealized_pnl >= 0 ? "text-[var(--color-signal-lime)]" : "text-[var(--color-ash)]"}`}>
                      {account?.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(account?.unrealized_pnl)}
                   </div>
                   <div className={`text-code-mono text-[11px] ${account?.unrealized_pnl_pct >= 0 ? "text-[var(--color-signal-lime)]" : "text-[var(--color-ash)]"}`}>
                      {formatPercent(account?.unrealized_pnl_pct)}
                   </div>
                </div>
             </div>

             {/* BUYING POWER */}
             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[32px] flex flex-col justify-between">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-6">BUYING POWER</div>
                <div className="text-code-mono text-[32px] font-normal text-[var(--color-chalk)] leading-none">{formatCurrency(account?.buying_power)}</div>
             </div>
          </div>
        </section>

        {/* POSITIONS TABLE */}
        <section>
          <div className="flex items-center justify-between mb-8">
            <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
              [ POSITIONS ]
            </div>
          </div>

          <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)]">
             {positions.length === 0 ? (
                <div className="p-10 text-center text-[var(--color-smoke)] text-ui-sans text-[13px]">No open positions</div>
             ) : (
                <div className="overflow-x-auto">
                   <table className="w-full text-left border-collapse">
                      <thead>
                         <tr className="border-b border-[var(--color-slate)]">
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium">SYMBOL</th>
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium text-right">SIDE</th>
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium text-right">QTY</th>
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium text-right">AVG PRICE</th>
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium text-right">CURRENT</th>
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium text-right">MKT VALUE</th>
                            <th className="p-[20px] text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] font-medium text-right">U P&L</th>
                         </tr>
                      </thead>
                      <tbody>
                         {positions.map((pos, idx) => {
                            const isGain = (pos.unrealized_pnl || 0) >= 0;
                            return (
                               <tr key={`${pos.symbol}-${idx}`} className="border-b border-[var(--color-graphite)] last:border-b-0 hover:bg-[var(--surface-hover)] transition-colors">
                                  <td className="p-[20px] text-ui-sans text-[13px] text-[var(--color-chalk)] font-medium">{pos.symbol}</td>
                                  <td className="p-[20px] text-right">
                                     <span className={`text-ui-sans text-[10px] uppercase font-medium tracking-[0.18em] border px-2 py-0.5 ${pos.side === 'LONG' || pos.side === 'BUY' ? 'border-[var(--color-signal-lime)] text-[var(--color-signal-lime)]' : 'border-[var(--color-chalk)] text-[var(--color-chalk)]'}`}>
                                        {pos.side || 'LONG'}
                                     </span>
                                  </td>
                                  <td className="p-[20px] text-code-mono text-[13px] text-[var(--color-chalk)] text-right">{pos.quantity}</td>
                                  <td className="p-[20px] text-code-mono text-[13px] text-[var(--color-smoke)] text-right">{formatCurrency(pos.avg_price)}</td>
                                  <td className="p-[20px] text-code-mono text-[13px] text-[var(--color-chalk)] text-right">{formatCurrency(pos.current_price)}</td>
                                  <td className="p-[20px] text-code-mono text-[13px] text-[var(--color-chalk)] text-right">{formatCurrency(pos.market_value || (pos.quantity * pos.current_price))}</td>
                                  <td className="p-[20px] text-right">
                                     <div className={`text-code-mono text-[13px] mb-0.5 ${isGain ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-ash)]'}`}>
                                        {isGain ? '+' : ''}{formatCurrency(pos.unrealized_pnl)}
                                     </div>
                                     <div className={`text-code-mono text-[10px] ${isGain ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-ash)]'}`}>
                                        {formatPercent(pos.unrealized_pnl_pct)}
                                     </div>
                                  </td>
                               </tr>
                            );
                         })}
                      </tbody>
                   </table>
                </div>
             )}
          </div>
        </section>

      </div>
    </div>
  );
}