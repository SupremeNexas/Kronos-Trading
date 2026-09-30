'use client';

import React, { useState, useEffect } from 'react';
import {
  Wallet,
  ShieldAlert,
  AlertCircle,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
  Send
} from 'lucide-react';
import { getPortfolio, getTradingAccount, getTradingPositions, placeOrder } from '@/lib/api';
import { cn } from '@/lib/utils';

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

  const [orderForm, setOrderForm] = useState({
    symbol: '',
    side: 'BUY',
    quantity: '',
    order_type: 'MARKET',
    price: ''
  });

  const [orderStatus, setOrderStatus] = useState<{type: 'success' | 'error' | null, message: string}>({type: null, message: ''});
  const [isSubmitting, setIsSubmitting] = useState(false);

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
      // Depending on actual response shape from API, adjust accordingly:
      const positionsData = posRes.data?.positions || posRes.data?.positions || [];
      setPositions(positionsData);
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

  const handleOrderSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setOrderStatus({ type: null, message: '' });

    // Validation
    if (!orderForm.symbol) return setOrderStatus({ type: 'error', message: 'Symbol is required' });
    const qty = Number(orderForm.quantity);
    if (isNaN(qty) || qty <= 0) return setOrderStatus({ type: 'error', message: 'Quantity must be greater than 0' });

    const price = Number(orderForm.price);
    if (orderForm.order_type === 'LIMIT' && (isNaN(price) || price <= 0)) {
       return setOrderStatus({ type: 'error', message: 'Valid price is required for Limit orders' });
    }

    setIsSubmitting(true);
    try {
      const orderPayload = {
        symbol: orderForm.symbol.toUpperCase(),
        side: orderForm.side,
        quantity: qty,
        order_type: orderForm.order_type,
        price: orderForm.order_type === 'MARKET' ? 0 : price
      };

      const res = await placeOrder(orderPayload);
      if (res.data?.success || res.data?.success) {
        setOrderStatus({ type: 'success', message: `Order placed: ${orderPayload.side} ${qty} ${orderPayload.symbol}` });
        setOrderForm({ symbol: '', side: 'BUY', quantity: '', order_type: 'MARKET', price: '' });
        // Refresh positions
        fetchData();
      } else {
        setOrderStatus({ type: 'error', message: res.data?.error || res.data?.error || 'Failed to place order' });
      }
    } catch (err: any) {
      setOrderStatus({ type: 'error', message: err.message || 'An error occurred while placing the order' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 md:p-8 space-y-8 font-sans">
      <header className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-3">
          <Wallet className="w-8 h-8 text-cyan-400" />
          <h1 className="text-3xl font-bold tracking-tight">Portfolio & Paper Trading</h1>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="p-2 bg-slate-800 rounded-full hover:bg-slate-700 transition"
          title="Refresh Data"
        >
          <RefreshCw className={cn("w-5 h-5 text-cyan-400", loading && "animate-spin")} />
        </button>
      </header>

      {/* PAPER TRADING BANNER */}
      <div className="bg-emerald-950/40 border border-emerald-500/50 rounded-lg p-4 flex items-center shadow-lg shadow-emerald-900/20">
        <ShieldAlert className="w-6 h-6 text-emerald-400 mr-3" />
        <div>
          <h2 className="text-emerald-300 font-semibold text-lg">PAPER TRADING MODE -- Zero Real Risk</h2>
          <p className="text-emerald-400/80 text-sm">All orders are simulated. Execution is based on current market data without real financial exposure.</p>
        </div>
      </div>

      {error ? (
        <div className="fintech-card bg-red-950/30 border border-red-500/50 p-6 flex flex-col items-center justify-center space-y-4 rounded-xl">
          <AlertCircle className="w-10 h-10 text-red-500" />
          <p className="text-red-200">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-slate-800 rounded-md text-sm font-medium hover:bg-slate-700 transition"
          >
            Retry
          </button>
        </div>
      ) : loading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(k => (
              <div key={k} className="fintech-card h-28 bg-slate-900/50 rounded-xl animate-pulse"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 fintech-card h-96 bg-slate-900/50 rounded-xl animate-pulse"></div>
            <div className="fintech-card h-96 bg-slate-900/50 rounded-xl animate-pulse"></div>
          </div>
        </div>
      ) : (
        <>
          {/* Account Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="fintech-card p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
                <Wallet className="w-16 h-16" />
              </div>
              <h3 className="text-slate-400 text-sm font-medium mb-1">Cash Balance</h3>
              <p className="text-2xl font-bold text-white">{formatCurrency(account?.cash_balance)}</p>
            </div>

            <div className="fintech-card p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-xl relative overflow-hidden group">
              <h3 className="text-slate-400 text-sm font-medium mb-1">Total Equity</h3>
              <p className="text-2xl font-bold text-white">{formatCurrency(account?.total_equity)}</p>
            </div>

            <div className="fintech-card p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-xl relative overflow-hidden group">
              <h3 className="text-slate-400 text-sm font-medium mb-1">Today's P&L</h3>
              <div className="flex items-center space-x-2">
                <p className={cn("text-2xl font-bold",
                  account?.today_pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                )}>
                  {account?.today_pnl >= 0 ? '+' : ''}{formatCurrency(account?.today_pnl)}
                </p>
                <div className={cn("flex items-center text-sm font-medium px-2 py-0.5 rounded-full",
                  account?.today_pnl_pct >= 0 ? "bg-emerald-400/10 text-emerald-400" : "bg-rose-400/10 text-rose-400"
                )}>
                  {account?.today_pnl_pct >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                  {formatPercent(account?.today_pnl_pct)}
                </div>
              </div>
            </div>

            <div className="fintech-card p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-xl relative overflow-hidden group">
              <h3 className="text-slate-400 text-sm font-medium mb-1">Buying Power</h3>
              <p className="text-2xl font-bold text-white">{formatCurrency(account?.buying_power)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Positions Table */}
            <div className="lg:col-span-2 fintech-card rounded-xl border border-slate-800 bg-slate-900/80 shadow-xl flex flex-col">
              <div className="p-5 border-b border-slate-800">
                <h3 className="text-lg font-semibold flex items-center">
                  Open Positions
                  <span className="ml-3 bg-slate-800 text-slate-300 text-xs px-2 py-1 rounded-md">{positions.length}</span>
                </h3>
              </div>
              <div className="p-0 overflow-x-auto">
                {positions.length === 0 ? (
                  <div className="p-10 text-center text-slate-500 flex flex-col items-center">
                    <Wallet className="w-12 h-12 mb-3 opacity-20" />
                    <p>No open positions</p>
                  </div>
                ) : (
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
                        <th className="p-4 font-medium">Symbol</th>
                        <th className="p-4 font-medium">Side</th>
                        <th className="p-4 font-medium text-right">Quantity</th>
                        <th className="p-4 font-medium text-right">Avg Price</th>
                        <th className="p-4 font-medium text-right">Current</th>
                        <th className="p-4 font-medium text-right">Market Value</th>
                        <th className="p-4 font-medium text-right">Unrealized P&L</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {positions.map((pos, idx) => {
                        const isGain = (pos.unrealized_pnl || 0) >= 0;
                        return (
                          <tr key={`${pos.symbol}-${idx}`} className="hover:bg-slate-800/30 transition">
                            <td className="p-4 font-bold">{pos.symbol}</td>
                            <td className="p-4">
                              <span className={cn(
                                "text-xs px-2 py-1 rounded font-semibold",
                                pos.side === 'LONG' || pos.side === 'BUY' ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                              )}>
                                {pos.side || 'LONG'}
                              </span>
                            </td>
                            <td className="p-4 text-right font-medium">{pos.quantity}</td>
                            <td className="p-4 text-right text-slate-300">{formatCurrency(pos.avg_price)}</td>
                            <td className="p-4 text-right text-slate-300">{formatCurrency(pos.current_price)}</td>
                            <td className="p-4 text-right font-medium">{formatCurrency(pos.market_value || (pos.quantity * pos.current_price))}</td>
                            <td className="p-4 text-right">
                              <div className={cn("font-medium", isGain ? "text-emerald-400" : "text-rose-400")}>
                                {isGain ? '+' : ''}{formatCurrency(pos.unrealized_pnl)}
                              </div>
                              <div className={cn("text-xs mt-0.5", isGain ? "text-emerald-500/70" : "text-rose-500/70")}>
                                {formatPercent(pos.unrealized_pnl_pct)}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            {/* Paper Trading Order Pad */}
            <div className="fintech-card rounded-xl border border-slate-800 bg-slate-900/80 shadow-xl flex flex-col h-fit">
              <div className="p-5 border-b border-slate-800 bg-slate-900/50 rounded-t-xl">
                <h3 className="text-lg font-semibold flex items-center">
                  Order Pad
                  <span className="ml-2 px-2 py-0.5 bg-slate-800 text-cyan-400 text-[10px] uppercase rounded tracking-wider border border-slate-700">Paper</span>
                </h3>
              </div>
              <div className="p-5">
                <form onSubmit={handleOrderSubmit} className="space-y-5">

                  {/* Symbol & Order Type */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Symbol</label>
                      <input
                        type="text"
                        value={orderForm.symbol}
                        onChange={(e) => setOrderForm({...orderForm, symbol: e.target.value.toUpperCase()})}
                        placeholder="e.g. AAPL"
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition font-mono uppercase"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Order Type</label>
                      <div className="flex bg-slate-950 rounded-lg border border-slate-800 overflow-hidden p-0.5">
                        <button
                          type="button"
                          onClick={() => setOrderForm({...orderForm, order_type: 'MARKET'})}
                          className={cn("flex-1 text-xs py-1.5 font-medium rounded-md transition",
                            orderForm.order_type === 'MARKET' ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-300"
                          )}
                        >
                          Market
                        </button>
                        <button
                          type="button"
                          onClick={() => setOrderForm({...orderForm, order_type: 'LIMIT'})}
                          className={cn("flex-1 text-xs py-1.5 font-medium rounded-md transition",
                            orderForm.order_type === 'LIMIT' ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-300"
                          )}
                        >
                          Limit
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Side Toggle */}
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Side</label>
                    <div className="flex space-x-2">
                      <button
                        type="button"
                        onClick={() => setOrderForm({...orderForm, side: 'BUY'})}
                        className={cn("flex-1 py-2 font-bold rounded-lg border transition",
                          orderForm.side === 'BUY'
                            ? "bg-emerald-500/20 border-emerald-500 text-emerald-400"
                            : "bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700"
                        )}
                      >
                        BUY
                      </button>
                      <button
                        type="button"
                        onClick={() => setOrderForm({...orderForm, side: 'SELL'})}
                        className={cn("flex-1 py-2 font-bold rounded-lg border transition",
                          orderForm.side === 'SELL'
                            ? "bg-rose-500/20 border-rose-500 text-rose-400"
                            : "bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700"
                        )}
                      >
                        SELL
                      </button>
                    </div>
                  </div>

                  {/* Quantity & Price */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Quantity</label>
                      <input
                        type="number"
                        min="1"
                        step="1"
                        value={orderForm.quantity}
                        onChange={(e) => setOrderForm({...orderForm, quantity: e.target.value})}
                        placeholder="Shares"
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition font-mono"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        {orderForm.order_type === 'MARKET' ? "Estimated Price" : "Execution Price"}
                      </label>
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        value={orderForm.price}
                        onChange={(e) => setOrderForm({...orderForm, price: e.target.value})}
                        placeholder="0.00"
                        disabled={orderForm.order_type === 'MARKET'}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition font-mono disabled:opacity-50 disabled:cursor-not-allowed"
                        required={orderForm.order_type === 'LIMIT'}
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={isSubmitting || !orderForm.symbol || !orderForm.quantity || (orderForm.order_type === 'LIMIT' && !orderForm.price)}
                      className={cn(
                        "w-full py-3 rounded-lg font-bold flex items-center justify-center transition",
                        isSubmitting ? "opacity-70 cursor-not-allowed" : "hover:shadow-[0_0_15px_rgba(34,211,238,0.3)]",
                        orderForm.side === 'BUY'
                          ? "bg-gradient-to-r from-emerald-600 to-emerald-500 text-white"
                          : "bg-gradient-to-r from-cyan-600 to-cyan-500 text-white"
                      )}
                    >
                      {isSubmitting ? (
                        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                      ) : (
                        <Send className="w-5 h-5 mr-2" />
                      )}
                      Submit {orderForm.side} Order
                    </button>
                  </div>

                  {/* Status Banner */}
                  {orderStatus.type && (
                    <div className={cn(
                      "p-3 rounded-lg text-sm flex items-start",
                      orderStatus.type === 'success' ? "bg-emerald-950/50 border border-emerald-900 text-emerald-400" : "bg-rose-950/50 border border-rose-900 text-rose-400"
                    )}>
                      {orderStatus.type === 'success' ? (
                        <CheckCircle2 className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      )}
                      <span className="flex-1 leading-snug">{orderStatus.message}</span>
                    </div>
                  )}
                </form>
              </div>
            </div>

          </div>
        </>
      )}
    </div>
  );
}
