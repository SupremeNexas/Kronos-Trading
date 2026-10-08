'use client';
import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';

export default function TacticDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      axios.get(`/api/tactics/${id}`, { withCredentials: true })
        .then(res => {
          if (res.data.success) {
            setData(res.data);
          }
        })
        .catch(e => console.error(e))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return <div className="p-8 text-[var(--color-chalk)]">Loading tactic details...</div>;
  if (!data) return <div className="p-8 text-[#ff4a4a]">Failed to load tactic or tactic not found.</div>;

  const { tactic, performance, assets, trades } = data;
  const tName = tactic?.name || performance?.tactic_name || id;

  return (
    <div className="p-8 max-w-7xl mx-auto text-[var(--color-chalk)] space-y-8">
      <div>
        <Link href="/tactics" className="text-[var(--color-smoke)] hover:text-white text-sm mb-4 inline-block">&larr; Back to Tactics</Link>
        <h1 className="text-3xl font-light font-serif text-[var(--color-signal-lime)]">{tName}</h1>
        {tactic?.description && <p className="text-[var(--color-smoke)] mt-2">{tactic.description}</p>}
      </div>

      {tactic && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
            <h3 className="text-sm tracking-widest text-[#888] mb-2 uppercase">Entry Rules</h3>
            <p className="text-sm font-mono">{tactic.entry_rules || 'None specified'}</p>
          </div>
          <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
            <h3 className="text-sm tracking-widest text-[#888] mb-2 uppercase">Exit Rules</h3>
            <p className="text-sm font-mono">{tactic.exit_rules || 'None specified'}</p>
          </div>
          <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
            <h3 className="text-sm tracking-widest text-[#888] mb-2 uppercase">Risk Rules</h3>
            <p className="text-sm font-mono">{tactic.risk_rules || 'None specified'}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="bg-[var(--surface-sunken)] border border-[var(--color-graphite)] p-4 text-center">
            <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-1">TRADES</div>
            <div className="text-xl font-bold">{performance.total_trades}</div>
        </div>
        <div className="bg-[var(--surface-sunken)] border border-[var(--color-graphite)] p-4 text-center">
            <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-1">WIN RATE</div>
            <div className="text-xl font-bold">{performance.win_rate}%</div>
        </div>
        <div className="bg-[var(--surface-sunken)] border border-[var(--color-graphite)] p-4 text-center border-l-2 border-l-[#444]">
            <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-1">TOTAL P&L</div>
            <div className={`text-xl font-bold ${performance.total_pnl > 0 ? 'text-[var(--color-signal-lime)]' : (performance.total_pnl < 0 ? 'text-[#ff4a4a]' : '')}`}>
                {performance.total_pnl > 0 ? '+' : (performance.total_pnl < 0 ? '-' : '')}${Math.abs(performance.total_pnl).toFixed(2)}
            </div>
        </div>
        <div className="bg-[var(--surface-sunken)] border border-[var(--color-graphite)] p-4 text-center">
            <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-1">RETURN</div>
            <div className={`text-xl font-bold ${performance.total_return_pct > 0 ? 'text-[var(--color-signal-lime)]' : (performance.total_return_pct < 0 ? 'text-[#ff4a4a]' : '')}`}>
                {performance.total_return_pct > 0 ? '+' : ''}{(performance.total_return_pct * 100).toFixed(2)}%
            </div>
        </div>
        <div className="bg-[var(--surface-sunken)] border border-[var(--color-graphite)] p-4 text-center">
            <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-1">AVG P&L</div>
            <div className={`text-xl font-bold ${performance.avg_pnl > 0 ? 'text-[var(--color-signal-lime)]' : (performance.avg_pnl < 0 ? 'text-[#ff4a4a]' : '')}`}>
                {performance.avg_pnl > 0 ? '+' : (performance.avg_pnl < 0 ? '-' : '')}${Math.abs(performance.avg_pnl).toFixed(2)}
            </div>
        </div>
        <div className="bg-[var(--surface-sunken)] border border-[var(--color-graphite)] p-4 text-center flex flex-col gap-1">
            <div className="flex justify-between text-xs">
                <span className="text-[var(--color-smoke)]">Best:</span>
                <span className="text-[var(--color-signal-lime)]">+{'$' + performance.best_trade?.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-xs">
                <span className="text-[var(--color-smoke)]">Worst:</span>
                <span className="text-[#ff4a4a]">{performance.worst_trade < 0 ? `-$${Math.abs(performance.worst_trade).toFixed(2)}` : '$0.00'}</span>
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-1 border border-[var(--color-graphite)] bg-[#111] p-0 self-start">
             <div className="p-4 border-b border-[var(--color-graphite)] bg-[var(--surface-sunken)]">
                 <h2 className="font-serif">Assets Traded</h2>
             </div>
             <div>
                {assets.length === 0 && <p className="p-4 text-sm text-[var(--color-smoke)]">No assets traded yet.</p>}
                {assets.map((a: any) => (
                    <div key={a.symbol} className="p-4 border-b border-[var(--color-graphite)]/50 last:border-0 hover:bg-[#1a1a1a] flex justify-between items-center text-sm">
                        <div>
                            <div className="font-bold">{a.symbol}</div>
                            <div className="text-[10px] text-[var(--color-smoke)]">{a.total_trades} trade{a.total_trades !== 1 ? 's' : ''}</div>
                        </div>
                        <div className={`font-mono text-right ${a.total_pnl > 0 ? 'text-[var(--color-signal-lime)]' : (a.total_pnl < 0 ? 'text-[#ff4a4a]' : '')}`}>
                            {a.total_pnl > 0 ? '+' : ''}${a.total_pnl.toFixed(2)}
                        </div>
                    </div>
                ))}
             </div>
          </div>
          
          <div className="md:col-span-3 border border-[var(--color-graphite)] bg-[#111] p-0">
             <div className="p-4 border-b border-[var(--color-graphite)] bg-[var(--surface-sunken)]">
                 <h2 className="font-serif">Trades from this Tactic</h2>
             </div>
             <div className="overflow-x-auto">
                 <table className="w-full text-sm text-left">
                   <thead>
                     <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                       <th className="py-2 pl-4">Date</th>
                       <th className="py-2">Symbol</th>
                       <th className="py-2">Side</th>
                       <th className="py-2">Qty</th>
                       <th className="py-2">P&L</th>
                       <th className="py-2">Return</th>
                       <th className="py-2">Reason</th>
                     </tr>
                   </thead>
                   <tbody>
                     {trades.length === 0 && (
                       <tr>
                         <td colSpan={7} className="py-4 text-center text-[var(--color-smoke)]">No trades found.</td>
                       </tr>
                     )}
                     {trades.map((t: any, i: number) => (
                       <tr key={i} className="border-b border-[var(--color-graphite)]/50 hover:bg-[#1a1a1a]">
                         <td className="py-2 pl-4 font-mono text-xs max-w-[120px] truncate" title={t.date}>{t.date}</td>
                         <td className="py-2 font-bold">{t.symbol}</td>
                         <td className={`py-2 ${t.side?.toUpperCase() === 'BUY' ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-signal-red)]'}`}>{t.side}</td>
                         <td className="py-2">{t.filled_quantity || t.quantity}</td>
                         <td className={`py-2 ${(t.realized_pnl || 0) > 0 ? 'text-[var(--color-signal-lime)]' : ((t.realized_pnl || 0) < 0 ? 'text-[#ff4a4a]' : '')}`}>
                           {t.realized_pnl ? (t.realized_pnl > 0 ? `+$${parseFloat(t.realized_pnl).toFixed(2)}` : `-$${Math.abs(parseFloat(t.realized_pnl)).toFixed(2)}`) : '-'}
                         </td>
                         <td className={`py-2 ${(t.realized_pnl_pct || 0) > 0 ? 'text-[var(--color-signal-lime)]' : ((t.realized_pnl_pct || 0) < 0 ? 'text-[#ff4a4a]' : '')}`}>
                           {t.realized_pnl_pct ? (t.realized_pnl_pct > 0 ? `+${(parseFloat(t.realized_pnl_pct)*100).toFixed(2)}%` : `${(parseFloat(t.realized_pnl_pct)*100).toFixed(2)}%`) : '-'}
                         </td>
                         <td className="py-2 font-mono text-xs text-[var(--color-ash)] max-w-[200px] truncate pr-4" title={t.reasoning || t.notes}>{t.reasoning || t.notes || '-'}</td>
                       </tr>
                     ))}
                   </tbody>
                 </table>
             </div>
          </div>
      </div>
    </div>
  );
}
