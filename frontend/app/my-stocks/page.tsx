'use client';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function MyStocks() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/trading/my-stocks', { withCredentials: true })
      .then(res => setStocks(res.data.stocks))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto text-[var(--color-chalk)] space-y-8">
      <h1 className="text-3xl font-light font-serif">My Assets & Tracker</h1>
      
      <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6 overflow-x-auto">
         {loading ? <p>Loading assets...</p> : (
           <table className="w-full text-sm text-left">
             <thead>
               <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                 <th className="py-2">Symbol</th>
                 <th className="py-2">Current Position</th>
                 <th className="py-2">Avg Entry</th>
                 <th className="py-2">Watched</th>
                 <th className="py-2">Last Trade</th>
               </tr>
             </thead>
             <tbody>
               {stocks.length === 0 && (
                 <tr>
                   <td colSpan={5} className="py-4 text-center text-[var(--color-smoke)]">No assets tracked yet.</td>
                 </tr>
               )}
               {stocks.map((s, i) => (
                 <tr key={i} className="border-b border-[var(--color-graphite)]/50 hover:bg-[var(--surface-hover)]">
                   <td className="py-2 font-bold">{s.symbol}</td>
                   <td className="py-2 text-[var(--color-signal-lime)]">{s.position}</td>
                   <td className="py-2">{s.avg_entry ? `$${s.avg_entry}` : '-'}</td>
                   <td className="py-2">{s.watched ? 'Yes' : 'No'}</td>
                   <td className="py-2 text-[var(--color-smoke)] text-xs">See /trades</td>
                 </tr>
               ))}
             </tbody>
           </table>
         )}
      </div>
    </div>
  );
}
