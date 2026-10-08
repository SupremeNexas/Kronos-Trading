'use client';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Trades() {
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTrades = () => {
    setLoading(true);
    axios.get('/api/trading/trades', { withCredentials: true })
      .then(res => setTrades(res.data.trades))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTrades();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto text-[var(--color-chalk)] space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-light font-serif">My Trades</h1>
        <button onClick={loadTrades} className="px-4 py-2 bg-[var(--surface-sunken)] border border-[var(--color-graphite)] hover:bg-[var(--surface-hover)]">Refresh</button>
      </div>
      
      <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6 overflow-x-auto">
         {loading ? <p>Loading trades...</p> : (
           <table className="w-full text-sm text-left">
             <thead>
               <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                 <th className="py-2">Date</th>
                 <th className="py-2">Symbol</th>
                 <th className="py-2">Tactic</th>
                 <th className="py-2">Side</th>
                 <th className="py-2">Qty</th>
                 <th className="py-2">Ord/Fill Qty</th>
                 <th className="py-2">P&L</th>
                 <th className="py-2">Return</th>
                 <th className="py-2">Status</th>
                 <th className="py-2">Reason</th>
               </tr>
             </thead>
             <tbody>
               {trades.length === 0 && (
                 <tr>
                   <td colSpan={10} className="py-4 text-center text-[var(--color-smoke)]">No trades found.</td>
                 </tr>
               )}
               {trades.map((t, i) => (
                 <tr key={i} className="border-b border-[var(--color-graphite)]/50 hover:bg-[var(--surface-hover)]">
                   <td className="py-2 font-mono text-xs max-w-[120px] truncate" title={t.date}>{t.date}</td>
                   <td className="py-2 font-bold">{t.symbol}</td>
                   <td className="py-2 font-mono text-xs">{t.tactic_name || t.tactic || "MANUAL"}</td>
                   <td className={`py-2 ${t.side?.toUpperCase() === 'BUY' ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-signal-red)]'}`}>{t.side}</td>
                   <td className="py-2">{t.quantity}</td>
                   <td className="py-2">{t.quantity} / {t.filled_quantity !== undefined ? t.filled_quantity : (t.status === 'FILLED' ? t.quantity : 0)}</td>
                   <td className={`py-2 ${(t.realized_pnl || 0) > 0 ? 'text-[var(--color-signal-lime)]' : ((t.realized_pnl || 0) < 0 ? 'text-[var(--color-signal-red)]' : '')}`}>
                     {t.realized_pnl ? (t.realized_pnl > 0 ? `+$${parseFloat(t.realized_pnl).toFixed(2)}` : `-$${Math.abs(parseFloat(t.realized_pnl)).toFixed(2)}`) : '-'}
                   </td>
                   <td className={`py-2 ${(t.realized_pnl_pct || 0) > 0 ? 'text-[var(--color-signal-lime)]' : ((t.realized_pnl_pct || 0) < 0 ? 'text-[var(--color-signal-red)]' : '')}`}>
                     {t.realized_pnl_pct ? (t.realized_pnl_pct > 0 ? `+${(parseFloat(t.realized_pnl_pct)*100).toFixed(2)}%` : `${(parseFloat(t.realized_pnl_pct)*100).toFixed(2)}%`) : '-'}
                   </td>
                   <td className="py-2">{t.status}</td>
                   <td className="py-2 font-mono text-xs text-[var(--color-ash)] max-w-[150px] truncate" title={t.reasoning}>{t.reasoning || t.notes || '-'}</td>
                 </tr>
               ))}
             </tbody>
           </table>
         )}
      </div>
    </div>
  );
}
