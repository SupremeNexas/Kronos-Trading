import re

with open("frontend/app/trades/page.tsx", "w") as f:
    f.write("""'use client';
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
                 <th className="py-2">Side</th>
                 <th className="py-2">Qty</th>
                 <th className="py-2">Filled Qty</th>
                 <th className="py-2">Order Type</th>
                 <th className="py-2">Limit Price</th>
                 <th className="py-2">Fill Price</th>
                 <th className="py-2">Status</th>
                 <th className="py-2">Alpaca ID</th>
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
                   <td className="py-2 font-mono text-xs">{t.date}</td>
                   <td className="py-2 font-bold">{t.symbol}</td>
                   <td className={`py-2 ${t.side?.toUpperCase() === 'BUY' ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-signal-red)]'}`}>{t.side}</td>
                   <td className="py-2">{t.quantity}</td>
                   <td className="py-2">{t.filled_quantity !== undefined ? t.filled_quantity : (t.status === 'FILLED' ? t.quantity : 0)}</td>
                   <td className="py-2">{t.order_type || 'MARKET'}</td>
                   <td className="py-2">{t.limit_price ? `$${parseFloat(t.limit_price).toFixed(2)}` : '-'}</td>
                   <td className="py-2">{t.fill_price ? `$${parseFloat(t.fill_price).toFixed(2)}` : '-'}</td>
                   <td className="py-2">{t.status}</td>
                   <td className="py-2 font-mono text-xs text-[var(--color-ash)]">{t.alpaca_order_id}</td>
                 </tr>
               ))}
             </tbody>
           </table>
         )}
      </div>
    </div>
  );
}
""")
