'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis
} from 'recharts';

export default function TradingLabPage() {
  const [activeTab, setActiveTab] = useState('DASHBOARD');
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [accuracy, setAccuracy] = useState<any>(null);

  useEffect(() => {
    fetchDashboard();
    fetchPredictions();
    fetchAccuracy();
    fetchTrades();
  }, []);
  const [trades, setTrades] = useState<any[]>([]);

  const fetchTrades = async () => {
    try {
      const res = await axios.get('/api/lab/trade-ledger');
      setTrades(res.data.data || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);


  const fetchDashboard = async () => {
    try {
      const res = await axios.get('/api/lab/system-status');
      setDashboardData(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchPredictions = async () => {
    try {
      const res = await axios.get('/api/lab/predictions');
      setPredictions(res.data.predictions || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAccuracy = async () => {
    try {
      const res = await axios.get('/api/journal/accuracy');
      setAccuracy(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full text-[var(--color-chalk)] pb-[120px]">
      <div className="w-full max-w-6xl mx-auto px-6 pt-[80px] space-y-[40px]">
        {/* BANNER */}
        <div className="bg-[var(--surface-card)] border border-[var(--color-signal-lime)] p-4 flex items-center justify-between">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-signal-lime)]">
            KRONOS PREDICTION & TRADING LAB (PAPER ONLY)
          </div>
          <div className="text-ui-sans text-[11px] uppercase tracking-[0.08em] text-[var(--color-ash)]">
            LIVE TRADING BLOCKED
          </div>
        </div>

        {/* TABS */}
        <div className="flex space-x-4 border-b border-[var(--color-graphite)] pb-2 overflow-x-auto text-ui-sans text-[11px] uppercase tracking-[0.1em]">
          {['DASHBOARD', 'PREDICTION LEDGER', 'TRADE OUTCOMES', 'TRADE LEDGER', 'MODEL SCORECARD'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 ${activeTab === tab ? 'text-[var(--color-signal-lime)] border-b-2 border-[var(--color-signal-lime)]' : 'text-[var(--color-smoke)] hover:text-[var(--color-ash)]'}`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* TAB CONTENTS */}
        {activeTab === 'DASHBOARD' && dashboardData && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[24px]">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.2em] text-[var(--color-smoke)] mb-4">SYSTEM STATUS</div>
                <div className="space-y-2 text-code-mono text-[14px]">
                  <div className="flex justify-between">
                    <span className="text-[var(--color-ash)]">Mode:</span>
                    <span className="text-[var(--color-signal-lime)]">{dashboardData.status.mode}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--color-ash)]">Broker:</span>
                    <span>{dashboardData.status.broker}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--color-ash)]">Provider:</span>
                    <span>{dashboardData.status.provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--color-ash)]">Model:</span>
                    <span>{dashboardData.status.model}</span>
                  </div>
                  <div className="flex justify-between mt-4 border-t border-[var(--color-graphite)] pt-2">
                    <span className="text-[var(--color-ash)]">Live Trading:</span>
                    <span className="text-[#ff4a4a]">DISABLED</span>
                  </div>
                </div>
              </section>

              <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[24px]">
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.2em] text-[var(--color-smoke)] mb-4">TODAY</div>
                <div className="grid grid-cols-2 gap-4 text-code-mono text-[18px]">
                  <div>
                    <div className="text-[var(--color-ash)] text-[12px] uppercase mb-1">Predictions</div>
                    {dashboardData.today.predictions}
                  </div>
                  <div>
                    <div className="text-[var(--color-ash)] text-[12px] uppercase mb-1">Trade Proposals</div>
                    {dashboardData.today.trade_proposals}
                  </div>
                  <div>
                    <div className="text-[var(--color-ash)] text-[12px] uppercase mb-1">Open Positions</div>
                    {dashboardData.today.open_positions}
                  </div>
                  <div>
                    <div className="text-[var(--color-ash)] text-[12px] uppercase mb-1">Win / Loss</div>
                    <span className="text-[var(--color-signal-lime)]">{dashboardData.today.wins}</span> / <span className="text-[#ff4a4a]">{dashboardData.today.losses}</span>
                  </div>
                  <div className="col-span-2 flex justify-between mt-4 border-t border-[var(--color-graphite)] pt-4">
                    <div>
                      <div className="text-[var(--color-ash)] text-[12px] uppercase mb-1">Realized P&L</div>
                      <span className={dashboardData.today.realized_pnl >= 0 ? "text-[var(--color-signal-lime)]" : "text-[#ff4a4a]"}>
                        {dashboardData.today.realized_pnl.toFixed(2)}%
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-[var(--color-ash)] text-[12px] uppercase mb-1">Unrealized P&L</div>
                      <span className={dashboardData.today.unrealized_pnl >= 0 ? "text-[var(--color-signal-lime)]" : "text-[#ff4a4a]"}>
                        {dashboardData.today.unrealized_pnl.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                </div>
              </section>
            </div>
            {/* Quick action: manually trigger a run */}
            <RunAgentPanel onComplete={fetchPredictions} />
          </div>
        )}

        {activeTab === 'PREDICTION LEDGER' && (
          <div className="space-y-4">
             <div className="text-ui-sans text-[12px] text-[var(--color-ash)]">
                Immutable record of every prediction before its future outcome is known.
             </div>
             <div className="overflow-x-auto border border-[var(--color-graphite)] text-code-mono text-[12px] bg-[var(--surface-card)]">
               <table className="w-full text-left">
                  <thead className="bg-[#1a1a1a] border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                    <tr>
                      <th className="p-3">TIME</th>
                      <th className="p-3">SYMBOL</th>
                      <th className="p-3">SIGNAL</th>
                      <th className="p-3">TARGET</th>
                      <th className="p-3">EX. RET</th>
                      <th className="p-3">CONF</th>
                      <th className="p-3">RISK</th>
                      <th className="p-3">OUTCOME</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictions.slice().reverse().map((p, i) => (
                      <tr key={i} className="border-b border-[var(--color-graphite)] hover:bg-[#222]">
                        <td className="p-3">{new Date(p.created_at).toLocaleString()}</td>
                        <td className="p-3">{p.symbol}</td>
                        <td className={`p-3 ${p.signal === 'BUY'||p.signal==='BULLISH' ? 'text-[var(--color-signal-lime)]' : p.signal==='HOLD' ? 'text-[var(--color-ash)]' : 'text-[#ff4a4a]'}`}>{p.signal}</td>
                        <td className="p-3">${p.forecast.target_price?.toFixed(2) || 'N/A'}</td>
                        <td className="p-3">{p.forecast.expected_return_pct?.toFixed(2)}%</td>
                        <td className="p-3">{(p.confidence * 100).toFixed(0)}%</td>
                        <td className="p-3">{p.validation?.verdict || p.risk_result?.status || 'N/A'}</td>
                        <td className="p-3">{p.outcome || 'PENDING'}</td>
                      </tr>
                    ))}
                  </tbody>
               </table>
             </div>
          </div>
        )}

        {activeTab === 'TRADE OUTCOMES' && (
          <div className="space-y-8">
             <div className="text-ui-sans text-[12px] text-[var(--color-ash)] mb-4">
                Comparison of Predicted Return vs Realized Return
             </div>
             
             {/* Chart container dummy */}
             <div className="h-[400px] w-full border border-[var(--color-graphite)] bg-[#111] flex items-center justify-center p-4">
                {predictions.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis type="number" dataKey="predicted" name="Predicted Return" unit="%" stroke="#888" domain={[-10, 10]} />
                      <YAxis type="number" dataKey="realized" name="Realized Return" unit="%" stroke="#888" domain={[-10, 10]} />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{backgroundColor: '#111', border: '1px solid #333', color: '#fff'}} />
                      <Scatter name="Predictions"
                        data={predictions.filter(p => typeof p.pnl_pct === 'number').map(p => ({
                          predicted: p.forecast?.expected_return_pct || 0,
                          realized: p.pnl_pct || 0,
                          symbol: p.symbol
                        }))}
                        fill="#a3e635" />
                    </ScatterChart>
                  </ResponsiveContainer>
                ) : (
                  <span className="text-[var(--color-smoke)]">No evaluation data available. Run the outcome engine.</span>
                )}
             </div>
          </div>
        )}

        
        {activeTab === 'TRADE LEDGER' && (
          <div className="space-y-4">
             <div className="text-ui-sans text-[12px] text-[var(--color-ash)]">
                Record of every paper-trading proposal and actual Alpaca paper order.
             </div>
             <div className="overflow-x-auto border border-[var(--color-graphite)] text-code-mono text-[12px] bg-[var(--surface-card)]">
               <table className="w-full text-left">
                  <thead className="bg-[#1a1a1a] border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                    <tr>
                      <th className="p-3">TIME</th>
                      <th className="p-3">SYMBOL</th>
                      <th className="p-3">SIDE</th>
                      <th className="p-3">QTY (PROP/ACT)</th>
                      <th className="p-3">TYPE</th>
                      <th className="p-3">PRICE</th>
                      <th className="p-3">ALPACA ID</th>
                      <th className="p-3">STATUS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.map((t, i) => (
                      <tr key={i} className="border-b border-[var(--color-graphite)] hover:bg-[#222]">
                        <td className="p-3">{new Date(t.created_at).toLocaleString()}</td>
                        <td className="p-3">{t.symbol}</td>
                        <td className={`p-3 ${t.side === 'BUY' ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>{t.side}</td>
                        <td className="p-3">{t.proposed_quantity?.toFixed(2)} / {t.filled_quantity?.toFixed(2) || '?'}</td>
                        <td className="p-3">{t.order_type}</td>
                        <td className="p-3">${t.actual_fill_price?.toFixed(2) || 'N/A'}</td>
                        <td className="p-3">{t.alpaca_order_id || 'N/A'}</td>
                        <td className="p-3">{t.order_status}</td>
                      </tr>
                    ))}
                  </tbody>
               </table>
             </div>
          </div>
        )}


        {activeTab === 'MODEL SCORECARD' && accuracy && (
          <div className="space-y-4">
             <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-code-mono text-[14px]">
                <div className="border border-[var(--color-graphite)] p-4 bg-[var(--surface-card)]">
                   <div className="text-[var(--color-smoke)] text-[11px] mb-2">DIRECTIONAL ACC</div>
                   <div className="text-[24px]">{accuracy.model_directional_accuracy}%</div>
                   <div className="text-[10px] text-[var(--color-ash)] mt-2">n={accuracy.resolved_trades}</div>
                </div>
                <div className="border border-[var(--color-graphite)] p-4 bg-[var(--surface-card)]">
                   <div className="text-[var(--color-smoke)] text-[11px] mb-2">WIN RATE</div>
                   <div className="text-[24px]">{accuracy.hit_rate_pct}%</div>
                </div>
                <div className="border border-[var(--color-graphite)] p-4 bg-[var(--surface-card)]">
                   <div className="text-[var(--color-smoke)] text-[11px] mb-2">AVG. PROFIT/LOSS</div>
                   <div className="text-[24px]">{accuracy.avg_pnl_pct}%</div>
                </div>
                <div className="border border-[var(--color-graphite)] p-4 bg-[var(--surface-card)]">
                   <div className="text-[var(--color-smoke)] text-[11px] mb-2">GATE BLOCKS</div>
                   <div className="text-[24px]">{accuracy.gate_blocked_trades}</div>
                </div>
             </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RunAgentPanel({ onComplete }: { onComplete: () => void }) {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [resData, setResData] = useState<any>(null);

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol) return;
    setLoading(true);
    setResData(null);
    try {
      const res = await axios.post('/api/agent_run', { symbol, timeframe: '1d', allow_trading: true });
      setResData(res.data);
      if (res.data.execution?.status === 'PENDING_CONFIRMATION') {
         // Auto-confirm for lab paper automation
         await axios.post('/api/trading/confirm_trade', { analysis_id: res.data.analysis_id || res.data.journal_id });
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
    onComplete();
  };

  return (
    <div className="border border-[var(--color-graphite)] p-[24px] bg-[var(--surface-card)]">
      <div className="text-ui-sans text-[11px] uppercase tracking-[0.2em] text-[var(--color-smoke)] mb-4">PAPER TRADING OPERATIONS</div>
      <form onSubmit={handleRun} className="flex gap-4">
        <input 
          value={symbol} onChange={e => setSymbol(e.target.value)} 
          placeholder="SYMBOL (e.g. AAPL)" 
          className="bg-transparent border border-[var(--color-graphite)] px-4 text-code-mono uppercase w-48 text-[14px]" 
        />
        <button type="submit" disabled={loading} className="border border-[var(--color-signal-lime)] text-[var(--color-signal-lime)] px-8 text-ui-sans text-[12px] uppercase">
           {loading ? 'RUNNING...' : 'FORECAST & TRADE (AUTO PAPER)'}
        </button>
      </form>
      {resData && (
        <div className="mt-6 text-code-mono text-[12px] p-4 bg-[#111] border border-[var(--color-graphite)] max-h-48 overflow-y-auto">
          {JSON.stringify(resData, null, 2)}
        </div>
      )}
    </div>
  );
}
