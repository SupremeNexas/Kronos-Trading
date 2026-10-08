'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import axios from 'axios';

function ManualTradingTerminalInner() {

  const [symbol, setSymbol] = useState('');
  const [priceData, setPriceData] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [account, setAccount] = useState<any>(null);
  const [positions, setPositions] = useState<any>(null);
  const [orders, setOrders] = useState<any>(null);

  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState(1);
  const [orderType, setOrderType] = useState('Market');
  const [limitPrice, setLimitPrice] = useState(0);

  const [tactics, setTactics] = useState<any[]>([]);
  const [selectedTactic, setSelectedTactic] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [notes, setNotes] = useState('');


  const searchParams = useSearchParams();
  const initSymbol = searchParams?.get('symbol') || '';
  const strategyParam = searchParams?.get('strategy') || '';
  const scanIdParam = searchParams?.get('scan_id') || '';
  const scoreParam = searchParams?.get('score') || '';
  const volParam = searchParams?.get('vol') || '';
  const attentionParam = searchParams?.get('attention') || '';
  const momentumParam = searchParams?.get('momentum') || '';
  
  useEffect(() => {
    if (initSymbol && !symbol) {
      setSymbol(initSymbol.toUpperCase());
      fetchSymbolData(initSymbol.toUpperCase());
    }
  }, [initSymbol]);

  
  useEffect(() => {
    fetchAccountData();
    axios.get('/api/tactics').then(res => {
        if(res.data.success) {
            setTactics(res.data.tactics);
            if (res.data.tactics.length > 0) setSelectedTactic(res.data.tactics[0].id);
        }
    }).catch(console.error);
    const interval = setInterval(fetchAccountData, 5000);
    return () => clearInterval(interval);
  }, []);


  const fetchSymbolData = async (sym: string) => {
    try {
      const [quoteRes, agentRes] = await Promise.all([
        axios.get(`/api/market/quote?symbol=${sym}`),
        axios.post('/api/agent_run', { symbol: sym, timeframe: '1d', allow_trading: false })
      ]);
      setPriceData(quoteRes.data);
      // agent_run returns a complex object: { analysis_id, execution, forecast, current_price, ... }
      setForecast(agentRes.data);
    } catch (e) {
      console.error(e);
      alert('Error fetching symbol data');
    }
  };

  const fetchAccountData = async () => {
    try {
      const [accRes, posRes, ordRes] = await Promise.all([
        axios.get('/api/trading/account'),
        axios.get('/api/trading/positions'),
        axios.get('/api/trading/orders')
      ]);
      setAccount(accRes.data);
      setPositions(posRes.data.positions);
      setOrders(ordRes.data.orders);
    } catch (e) {
      console.error(e);
    }
  };

  const handlePlaceOrder = async () => {
    if (!confirm(`Confirm ${side} ${quantity} ${symbol} @ ${orderType}?`)) return;
    try {
      let tName = tactics.find(t=>t.id === selectedTactic)?.name || '';
      const payload = {
        symbol,
        side,
        quantity,
        order_type: orderType,
        price: orderType === 'Limit' ? limitPrice : 0,
        tactic_id: selectedTactic,
        tactic_name: tName,
        reasoning,
        notes,
        analysis_id: forecast?.analysis_id,
        strategy: strategyParam || undefined,
        signal_scan_id: scanIdParam || undefined,
        signal_score: scoreParam || undefined,
        volume_ratio: volParam || undefined,
        attention_score: attentionParam || undefined,
        momentum_7d: momentumParam || undefined,
        decision: strategyParam ? "MANUAL_TRADE" : undefined
      };
      const res = await axios.post('/api/trading/place-order', payload);
      if (res.data.success) {
        alert('Order submitted in PAPER mode!');
        fetchAccountData();
      } else {
        alert('Order failed: ' + res.data.error);
      }
    } catch (e) {
      console.error(e);
      alert('Order submission error');
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (!confirm(`Cancel order ${orderId}?`)) return;
    try {
       const res = await axios.post('/api/trading/cancel-order', { order_id: orderId });
       if (res.data.success) {
           alert('Order cancelled');
           fetchAccountData();
       } else {
           alert('Cancel failed: ' + res.data.error);
       }
    } catch (e) {
       console.error(e);
       alert('Order cancel error');
    }
  };

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full text-[var(--color-chalk)] pb-[120px] p-6">
      <div className="max-w-7xl mx-auto space-y-6 pt-10">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-heading-sm font-light text-[var(--color-signal-lime)]">MANUAL TRADING TERMINAL</h1>
          <div className="border border-[#ff4a4a] text-[#ff4a4a] px-4 py-2 text-ui-sans text-[12px] tracking-widest uppercase font-bold animate-pulse shadow-[0_0_8px_rgba(255,74,74,0.4)]">
             PAPER TRADING ACCOUNT ACTIVE
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* LEFT: Search & Forecast & Trade Ticket */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
                <input
                  value={symbol} onChange={e => {setSymbol(e.target.value.toUpperCase());}}
                  placeholder="ENTER SYMBOL (e.g. AAPL)"
                  className="w-full bg-transparent border-b border-[var(--color-graphite)] py-2 text-code-mono uppercase text-[18px] focus:outline-none focus:border-[var(--color-signal-lime)]"
                />
                <button onClick={() => fetchSymbolData(symbol)} className="mt-4 w-full border border-[var(--color-smoke)] py-2 text-ui-sans text-[12px] uppercase tracking-widest text-[var(--color-smoke)] hover:text-white hover:border-white"> Fetch Data </button>
            </div>

            {priceData && (
              <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
                 <div className="text-subheading">{symbol}</div>
                 <div className="text-code-mono text-[24px]">${priceData.price?.toFixed(2)}</div>
              </div>
            )}

            {forecast && forecast.forecast && (
              <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
                <div className="text-ui-sans uppercase text-[11px] mb-2 text-[var(--color-smoke)]">KRONOS FORECAST</div>
                <div className="text-code-mono">Target: ${forecast.forecast.target_price?.toFixed(2)}</div>
                <div className="text-code-mono">Signal: {forecast.forecast.direction || forecast.forecast.forecast_direction} ({forecast.forecast.expected_return_pct > 0 ? '+' : ''}{(forecast.forecast.expected_return_pct * 100)?.toFixed(2)}%)</div>
                <div className="text-[10px] text-[var(--color-smoke)] mt-2">ID: {forecast.analysis_id}</div>
              </div>
            )}

            {/* TRADING TICKET */}
            {symbol && (
              <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6 space-y-4">
                 <div className="flex gap-2">
                    <button onClick={() => setSide('BUY')} className={`flex-1 py-3 ${side === 'BUY' ? 'bg-[var(--color-signal-lime)] text-black' : 'border border-[var(--color-graphite)]'}`}>BUY</button>
                    <button onClick={() => setSide('SELL')} className={`flex-1 py-3 ${side === 'SELL' ? 'bg-[#ff4a4a] text-black' : 'border border-[var(--color-graphite)]'}`}>SELL</button>
                 </div>
                 <input type="number" value={quantity} onChange={e => setQuantity(Number(e.target.value))} placeholder="Qty" className="w-full bg-transparent border border-[var(--color-graphite)] p-3 text-code-mono" />
                 <select value={orderType} onChange={e => setOrderType(e.target.value)} className="w-full bg-[#111] p-3 border border-[var(--color-graphite)] text-code-mono">
                    <option>Market</option>
                    <option>Limit</option>
                 </select>
                 {orderType === 'Limit' && <input type="number" value={limitPrice} onChange={e => setLimitPrice(Number(e.target.value))} placeholder="Limit Price" className="w-full bg-transparent border border-[var(--color-graphite)] p-3 text-code-mono" />}
                 <button onClick={handlePlaceOrder} className={`w-full py-4 text-ui-sans text-[14px] uppercase tracking-widest ${side === 'BUY' ? 'bg-[var(--color-signal-lime)] text-black' : 'bg-[#ff4a4a] text-black'}`}>Submit {side} Order</button>
              </div>
            )}
          </div>

          {/* RIGHT: ACCOUNT & POSITIONS */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
                <div className="text-ui-sans uppercase text-[11px] mb-4 text-[var(--color-smoke)]">ACCOUNT SUMMARY</div>
                {account && (
                  <div className="grid grid-cols-4 gap-4 text-code-mono text-[16px]">
                    <div><div className="text-[var(--color-ash)] text-[10px]">CASH</div>${account.cash?.toFixed(2)}</div>
                    <div><div className="text-[var(--color-ash)] text-[10px]">BUYING POWER</div>${account.buying_power?.toFixed(2)}</div>
                    <div><div className="text-[var(--color-ash)] text-[10px]">EQUITY</div>${account.portfolio_value?.toFixed(2)}</div>
                    <div><div className="text-[var(--color-ash)] text-[10px]">DAY PNL</div>
                      <span className={account.day_pnl >= 0 ? "text-[var(--color-signal-lime)]" : "text-[#ff4a4a]"}>
                        ${account.day_pnl?.toFixed(2)}
                      </span>
                    </div>
                  </div>
                )}
             </div>

             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-0 pb-6 border-b-0 space-y-4">
                <div className="px-6 pt-6 text-ui-sans uppercase text-[11px] text-[var(--color-smoke)]">POSITIONS</div>
                <div className="overflow-x-auto text-code-mono text-[12px] w-full">
                  <table className="w-full text-left">
                    <thead className="bg-[#1a1a1a] border-b border-t border-[var(--color-graphite)] text-[var(--color-smoke)]">
                      <tr>
                        <th className="p-3 pl-6">SYMBOL</th>
                        <th className="p-3">QTY</th>
                        <th className="p-3">AVG PRICE</th>
                        <th className="p-3">CURRENT</th>
                        <th className="p-3">MKT VALUE</th>
                        <th className="p-3">UNREALIZED</th>
                        <th className="p-3 pr-6">DAY PNL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {!positions || positions.length === 0 ? (
                        <tr><td colSpan={7} className="p-6 text-center text-[var(--color-smoke)] border-b border-[var(--color-graphite)]">No open positions</td></tr>
                      ) : positions.map((p: any, i: number) => (
                        <tr key={i} className="border-b border-[var(--color-graphite)] hover:bg-[#222]">
                          <td className="p-3 pl-6 font-bold">{p.symbol}</td>
                          <td className="p-3">{p.quantity}</td>
                          <td className="p-3">${p.average_price?.toFixed(2)}</td>
                          <td className="p-3">${p.current_price?.toFixed(2)}</td>
                          <td className="p-3">${p.market_value?.toFixed(2)}</td>
                          <td className={`p-3 ${p.total_pnl >= 0 ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                            ${p.total_pnl?.toFixed(2)} ({p.pnl_pct?.toFixed(2)}%)
                          </td>
                          <td className={`p-3 pr-6 ${p.day_pnl >= 0 ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                            ${p.day_pnl?.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
             </div>

             {/* ORDERS */}
             <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-0 pb-6 border-b-0 space-y-4">
                <div className="px-6 pt-6 text-ui-sans uppercase text-[11px] text-[var(--color-smoke)]">RECENT ORDERS</div>
                <div className="overflow-x-auto text-code-mono text-[12px] w-full">
                  <table className="w-full text-left">
                    <thead className="bg-[#1a1a1a] border-b border-t border-[var(--color-graphite)] text-[var(--color-smoke)]">
                      <tr>
                        <th className="p-3 pl-6">TIME</th>
                        <th className="p-3">SYMBOL</th>
                        <th className="p-3">SIDE</th>
                        <th className="p-3">QTY / FILLED</th>
                        <th className="p-3">TYPE</th>
                        <th className="p-3">STATUS</th>
                        <th className="p-3">ALPACA ID</th>
                        <th className="p-3 pr-6">ACTION</th>
                      </tr>
                    </thead>
                    <tbody>
                      {!orders || orders.length === 0 ? (
                         <tr><td colSpan={8} className="p-6 text-center text-[var(--color-smoke)] border-b border-[var(--color-graphite)]">No recent orders</td></tr>
                      ) : orders.map((o: any, i: number) => (
                        <tr key={i} className="border-b border-[var(--color-graphite)] hover:bg-[#222]">
                          <td className="p-3 pl-6">{new Date(o.time).toLocaleString()}</td>
                          <td className="p-3 font-bold">{o.symbol}</td>
                          <td className={`p-3 ${o.side === 'buy' ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>{o.side.toUpperCase()}</td>
                          <td className="p-3">{o.quantity} / {o.filled_quantity}</td>
                          <td className="p-3">{o.order_type.toUpperCase()}</td>
                          <td className="p-3">{o.status.toUpperCase()}</td>
                          <td className="p-3 text-[10px] text-[var(--color-smoke)]">{o.order_id}</td>
                          <td className="p-3 pr-6">
                            {(o.status === 'new' || o.status === 'accepted' || o.status === 'partially_filled') && (
                                <button onClick={() => handleCancelOrder(o.order_id)} className="text-[#ff4a4a] border border-[#ff4a4a] px-2 py-1 text-[10px]">CANCEL</button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { Suspense } from 'react';

export default function ManualTradingTerminal() {
  return (
    <Suspense fallback={<div>Loading terminal...</div>}>
      <ManualTradingTerminalInner />
    </Suspense>
  );
}
