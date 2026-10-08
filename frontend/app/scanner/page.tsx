'use client';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function OpportunityScanner() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastScan, setLastScan] = useState('');

  const runScan = async () => {
    setLoading(true);
    try {
      const res = await axios.post('/api/scanner/dynamic-alpaca', {}, { withCredentials: true });
      if (res.data.success) {
        setOpportunities(res.data.opportunities);
        setLastScan(new Date().toLocaleTimeString());
      } else {
        alert(res.data.error || 'Failed to scan');
      }
    } catch (e) {
      console.error(e);
      alert('Error running scan');
    }
    setLoading(false);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto text-[var(--color-chalk)] space-y-8">
      <div className="flex justify-between items-center bg-[#111] p-6 border border-[var(--color-graphite)] shadow-md">
        <div>
          <h1 className="text-3xl font-light font-serif text-[var(--color-chalk)]">Live Opportunity Scanner</h1>
          <p className="text-sm text-[var(--color-smoke)] mt-2">Dynamic discovery across entire Alpaca PAPER asset universe.</p>
        </div>
        <button 
          onClick={runScan} 
          disabled={loading}
          className="px-6 py-3 rounded-md bg-[var(--color-signal-lime)] text-[#111] font-bold tracking-widest hover:bg-[#86e24b] disabled:opacity-50"
        >
          {loading ? 'SCANNING UNIVERSE...' : 'RUN LIVE SCAN'}
        </button>
      </div>
      
      {lastScan && <p className="text-[12px] text-[var(--color-ash)] my-4">Last scan completed at: {lastScan}</p>}

      <div className="bg-[#111] border border-[var(--color-graphite)] overflow-x-auto shadow-sm">
        <table className="w-full text-sm text-left">
          <thead className="bg-[#1a1a1a]">
            <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
              <th className="py-4 pl-6 uppercase tracking-wider text-[11px]">Asset</th>
              <th className="py-4 uppercase tracking-wider text-[11px]">Class</th>
              <th className="py-4 uppercase tracking-wider text-[11px]">Detected Tactic</th>
              <th className="py-4 uppercase tracking-wider text-[11px]">Setup Score</th>
              <th className="py-4 uppercase tracking-wider text-[11px]">Risk/Reward</th>
              <th className="py-4 uppercase tracking-wider text-[11px]">Risk Status</th>
              <th className="py-4 pr-6 uppercase tracking-wider text-[11px]">Reason</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.length === 0 && !loading && (
              <tr>
                <td colSpan={7} className="py-8 text-center text-lg text-[var(--color-smoke)]">
                  Click 'Run Live Scan' to dynamically search Alpaca asset universe for valid setups.
                </td>
              </tr>
            )}
            {opportunities.length > 0 && !loading && opportunities.map((opp, idx) => (
              <tr key={idx} className="border-b border-[var(--color-graphite)]/50 hover:bg-[#1a1a1a] transition-colors">
                <td className="py-4 pl-6 font-bold">{opp.asset}</td>
                <td className="py-4 text-[var(--color-smoke)]">{opp.asset_class}</td>
                <td className="py-4 font-mono text-xs font-semibold">{opp.tactic_name}</td>
                <td className="py-4">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[var(--color-signal-lime)]">{opp.score}/100</span>
                    <div className="w-16 h-1.5 bg-[#222]">
                      <div className="h-full bg-[var(--color-signal-lime)]" style={{ width: `${opp.score}%` }}></div>
                    </div>
                  </div>
                </td>
                <td className="py-4 text-[var(--color-smoke)]">{opp.risk_reward}</td>
                <td className={`py-4 font-bold ${opp.risk_status === 'APPROVED' ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                  {opp.risk_status}
                </td>
                <td className="py-4 pr-6 text-xs text-[var(--color-smoke)] max-w-xs">{opp.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
