'use client';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function TacticsDashboard() {
  const [tactics, setTactics] = useState<any[]>([]);
  const [performance, setPerformance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const pRes = await axios.get('/api/tactics/performance', { withCredentials: true });
      const tRes = await axios.get('/api/tactics', { withCredentials: true });
      if(pRes.data.success) setPerformance(pRes.data.performance);
      if(tRes.data.success) setTactics(tRes.data.tactics);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalTrades = performance.reduce((sum, p) => sum + p.total_trades, 0);
  const totalPnL = performance.reduce((sum, p) => sum + p.total_pnl, 0);
  const totalWins = performance.reduce((sum, p) => sum + p.winning_trades, 0);
  const overallWinRate = totalTrades > 0 ? ((totalWins / totalTrades) * 100).toFixed(2) + '%' : '0.00%';

  let bestTactic = { tactic_name: 'None', total_pnl: 0 };
  let worstTactic = { tactic_name: 'None', total_pnl: 0 };
  if (performance.length > 0) {
      const sorted = [...performance].sort((a,b) => b.total_pnl - a.total_pnl);
      bestTactic = sorted[0];
      worstTactic = sorted[sorted.length - 1];
  }

  return (
    <div className="p-8 max-w-7xl mx-auto text-[var(--color-chalk)] space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-light font-serif">Tactic Performance Dashboard</h1>
        <button onClick={loadData} className="px-4 py-2 bg-[var(--surface-sunken)] border border-[var(--color-graphite)] hover:bg-[var(--surface-hover)]">Refresh</button>
      </div>

      {loading ? <p>Loading performance...</p> : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-[#111] border border-[var(--color-graphite)] p-6 text-center">
                <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-2">TOTAL P&L</div>
                <div className={`text-2xl font-bold ${totalPnL >= 0 ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                    {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}
                </div>
            </div>
            <div className="bg-[#111] border border-[var(--color-graphite)] p-6 text-center">
                <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-2">TOTAL TRADES</div>
                <div className="text-2xl font-bold text-white">{totalTrades}</div>
            </div>
            <div className="bg-[#111] border border-[var(--color-graphite)] p-6 text-center">
                <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-2">OVERALL WIN RATE</div>
                <div className="text-2xl font-bold text-white">{overallWinRate}</div>
            </div>
            <div className="bg-[#111] border border-[var(--color-graphite)] p-6 text-center">
                <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-2">BEST TACTIC</div>
                <div className="text-sm font-bold text-[var(--color-signal-lime)] truncate">{bestTactic.tactic_name || 'N/A'}</div>
                <div className="text-xs text-[var(--color-smoke)]">${bestTactic.total_pnl.toFixed(2)}</div>
            </div>
            <div className="bg-[#111] border border-[var(--color-graphite)] p-6 text-center">
                <div className="text-[10px] text-[var(--color-smoke)] tracking-widest mb-2">WORST TACTIC</div>
                <div className="text-sm font-bold text-[#ff4a4a] truncate">{worstTactic.tactic_name || 'N/A'}</div>
                <div className="text-xs text-[var(--color-smoke)]">${worstTactic.total_pnl.toFixed(2)}</div>
            </div>
          </div>

          <h2 className="text-xl mt-12 mb-4 font-serif">Tactic Comparison</h2>
          <div className="bg-[#111] border border-[var(--color-graphite)] overflow-x-auto">
             <table className="w-full text-sm text-left">
               <thead>
                 <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)] bg-[#1a1a1a]">
                   <th className="py-4 pl-4">Tactic Name</th>
                   <th className="py-4 text-right">Trades (W/L)</th>
                   <th className="py-4 text-right">Win Rate</th>
                   <th className="py-4 text-right">Total P&L</th>
                   <th className="py-4 text-right">Total Return</th>
                   <th className="py-4 text-right">Avg P&L</th>
                   <th className="py-4 text-right">Best Trade</th>
                   <th className="py-4 text-right pr-4">Worst Trade</th>
                 </tr>
               </thead>
               <tbody>
                 {performance.length === 0 && (
                   <tr>
                     <td colSpan={8} className="py-6 text-center text-[var(--color-smoke)]">NO DATA</td>
                   </tr>
                 )}
                 {performance.sort((a,b) => b.total_pnl - a.total_pnl).map((p, i) => (
                   <tr key={i} className="border-b border-[var(--color-graphite)]/50 hover:bg-[#1a1a1a] cursor-pointer" onClick={() => window.location.href = `/tactics/${p.tactic_id}`}>
                     <td className="py-4 pl-4 font-bold">{p.tactic_name}</td>
                     <td className="py-4 text-right">{p.total_trades} (<span className="text-[var(--color-signal-lime)]">{p.winning_trades}</span>/<span className="text-[#ff4a4a]">{p.losing_trades}</span>)</td>
                     <td className="py-4 text-right">{p.win_rate}%</td>
                     <td className={`py-4 text-right font-bold ${p.total_pnl > 0 ? 'text-[var(--color-signal-lime)]' : (p.total_pnl < 0 ? 'text-[#ff4a4a]' : '')}`}>
                       {p.total_pnl > 0 ? '+' : (p.total_pnl < 0 ? '-' : '')}${Math.abs(p.total_pnl).toFixed(2)}
                     </td>
                     <td className={`py-4 text-right ${p.total_return_pct > 0 ? 'text-[var(--color-signal-lime)]' : (p.total_return_pct < 0 ? 'text-[#ff4a4a]' : '')}`}>
                       {p.total_return_pct > 0 ? '+' : ''}{(p.total_return_pct * 100).toFixed(2)}%
                     </td>
                     <td className={`py-4 text-right ${p.avg_pnl > 0 ? 'text-[var(--color-signal-lime)]' : (p.avg_pnl < 0 ? 'text-[#ff4a4a]' : '')}`}>
                       {p.avg_pnl > 0 ? '+' : (p.avg_pnl < 0 ? '-' : '')}${Math.abs(p.avg_pnl).toFixed(2)}
                     </td>
                     <td className="py-4 text-right text-[var(--color-signal-lime)]">{p.best_trade > 0 ? `+$${p.best_trade.toFixed(2)}` : (p.best_trade < 0 ? `-$${Math.abs(p.best_trade).toFixed(2)}` : '$0.00')}</td>
                     <td className="py-4 text-right text-[#ff4a4a] pr-4">{p.worst_trade > 0 ? `+$${p.worst_trade.toFixed(2)}` : (p.worst_trade < 0 ? `-$${Math.abs(p.worst_trade).toFixed(2)}` : '$0.00')}</td>
                   </tr>
                 ))}
               </tbody>
             </table>
          </div>

          <h2 className="text-xl mt-12 mb-4 font-serif">All Tactics Inventory</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tactics.map((t: any) => (
                <div key={t.id} className="bg-[#111] border border-[var(--color-graphite)] p-6">
                    <h3 className="text-lg font-bold mb-2">{t.name} <span className="text-[10px] text-[#888] font-mono font-normal ml-2">{t.id}</span></h3>
                    <p className="text-[13px] text-[var(--color-smoke)] mb-4">{t.description}</p>
                    <div className="grid grid-cols-2 gap-4 text-[11px]">
                        <div><span className="text-[#888]">Source:</span> {t.source}</div>
                        <div><span className="text-[#888]">Entry:</span> {t.entry_rules}</div>
                        <div><span className="text-[#888]">Exit:</span> {t.exit_rules}</div>
                        <div><span className="text-[#888]">Risk:</span> {t.risk_rules}</div>
                    </div>
                </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
