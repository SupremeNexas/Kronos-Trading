'use client';

import { useState, useEffect, useCallback } from 'react';
import { Star, Bell, Trash2, Plus, AlertCircle, Loader2 } from 'lucide-react';
import {
  getWatchlists,
  addWatchlistItem,
  removeWatchlistItem,
  getAlerts,
  createAlert,
  deleteAlert,
  getMarketQuote
} from '@/lib/api';

const USER_ID = "user_demo_001";

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newSymbol, setNewSymbol] = useState('');
  const [newAlertType, setNewAlertType] = useState('PRICE_ABOVE');
  const [newTargetPrice, setNewTargetPrice] = useState('');
  const [newAlertSymbol, setNewAlertSymbol] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [wlRes, alRes] = await Promise.all([
        getWatchlists(USER_ID),
        getAlerts(USER_ID)
      ]);

      // Enrich watchlist with live quotes
      const wlWithQuotes = await Promise.all(
        wlRes.data.watchlists.map(async (item: any) => {
          try {
            const quote = await getMarketQuote(item.symbol);
            return { ...item, quote: quote.data };
          } catch {
            return { ...item, quote: null };
          }
        })
      );

      setWatchlist(wlWithQuotes);
      setAlerts(alRes.data.alerts);
    } catch (err) {
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAddWatchlist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol) return;
    try {
      await addWatchlistItem(USER_ID, newSymbol.toUpperCase());
      setNewSymbol('');
      fetchData();
    } catch {
      alert('Failed to add symbol');
    }
  };

  const handleRemoveWatchlist = async (symbol: string) => {
    try {
      await removeWatchlistItem(USER_ID, symbol);
      fetchData();
    } catch {
      alert('Failed to remove symbol');
    }
  };

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAlertSymbol || !newTargetPrice) return;
    try {
      await createAlert(USER_ID, newAlertSymbol.toUpperCase(), newAlertType, parseFloat(newTargetPrice), `${newAlertType} ${newTargetPrice}`);
      setNewAlertSymbol('');
      setNewTargetPrice('');
      fetchData();
    } catch {
      alert('Failed to create alert');
    }
  };

  const handleDeleteAlert = async (alertId: string) => {
    try {
      await deleteAlert(USER_ID, alertId);
      fetchData();
    } catch {
      alert('Failed to delete alert');
    }
  };

  if (loading) return <div className="flex h-screen items-center justify-center text-[var(--color-chalk)] bg-[var(--surface-canvas)]"><div className="text-ui-sans text-[11px] tracking-[0.2em] text-[var(--color-smoke)] uppercase">Loading Watchlist...</div></div>;

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[80px]">

        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ RESEARCH WATCHLIST ]
          </div>
          
          <div className="flex justify-between items-end mb-8 border-b border-[var(--color-graphite)] pb-8">
            <h2 className="text-display-serif font-light text-[49px] leading-[1.05] tracking-[-1px] text-[var(--color-chalk)]">
              Tracked <span className="italic text-[var(--color-signal-lime)]">Assets.</span>
            </h2>
            <form onSubmit={handleAddWatchlist} className="flex gap-[16px] items-center">
              <input
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
                placeholder="AAPL..."
                className="bg-transparent border border-[var(--color-slate)] p-2 text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none uppercase w-32"
              />
              <button className="px-[32px] h-[44px] bg-[var(--color-signal-lime)] text-[var(--color-void-black)] text-ui-sans text-[13px] font-medium tracking-[0.08em] uppercase transition-transform active:scale-95 glow-signal">
                ADD
              </button>
            </form>
          </div>

          {watchlist.length === 0 ? (
            <p className="text-ui-sans text-[13px] text-[var(--color-smoke)] py-8 border-b border-[var(--color-graphite)]">Your watchlist is empty.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[20px]">
              {watchlist.map((item) => (
                <div key={item.symbol} className="bg-[var(--surface-raised)] border border-[var(--color-graphite)] p-[24px] flex flex-col justify-between group">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <div className="text-ui-sans text-[13px] font-medium text-[var(--color-chalk)]">{item.symbol}</div>
                      <div className="text-ui-sans text-[10px] uppercase font-medium tracking-[0.18em] text-[var(--color-smoke)]">{item.name}</div>
                    </div>
                    <button onClick={() => handleRemoveWatchlist(item.symbol)} className="text-[var(--color-smoke)] hover:text-[#ff4a4a] transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div>
                    {item.quote ? (
                      <>
                        <div className="text-code-mono text-[24px] font-normal text-[var(--color-chalk)] leading-none mb-2">
                           ${item.quote.price.toFixed(2)}
                        </div>
                        <div className={`text-code-mono text-[11px] font-normal ${item.quote.change >= 0 ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                           {item.quote.change > 0 ? '+' : ''}{item.quote.change.toFixed(2)} ({item.quote.change_pct.toFixed(2)}%)
                        </div>
                      </>
                    ) : (
                      <div className="text-ui-sans text-[11px] uppercase text-[var(--color-smoke)]">N/A</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ ACTIVE ALERTS ]
          </div>
          
          <form onSubmit={handleCreateAlert} className="flex flex-col md:flex-row gap-[16px] items-end border-b border-[var(--color-graphite)] pb-8 mb-8">
            <div className="flex flex-col gap-2 w-full md:max-w-xs">
              <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">SYMBOL</label>
              <input
                value={newAlertSymbol}
                onChange={(e) => setNewAlertSymbol(e.target.value)}
                placeholder="AAPL"
                className="bg-transparent border border-[var(--color-slate)] p-2 text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none uppercase"
              />
            </div>
            <div className="flex flex-col gap-2 w-full md:max-w-xs">
              <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">CONDITION</label>
              <select
                value={newAlertType}
                onChange={(e) => setNewAlertType(e.target.value)}
                className="bg-[var(--surface-raised)] border border-[var(--color-slate)] p-2 text-code-mono text-[14px] text-[var(--color-chalk)] focus:outline-none h-[42px]"
              >
                <option value="PRICE_ABOVE">PRICE ABOVE</option>
                <option value="PRICE_BELOW">PRICE BELOW</option>
              </select>
            </div>
            <div className="flex flex-col gap-2 w-full md:max-w-xs">
              <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">TARGET PRICE</label>
              <input
                type="number"
                value={newTargetPrice}
                onChange={(e) => setNewTargetPrice(e.target.value)}
                placeholder="0.00"
                className="bg-transparent border border-[var(--color-slate)] p-2 text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none"
              />
            </div>
            <button className="px-[32px] h-[44px] bg-[var(--surface-raised)] border border-[var(--color-slate)] text-[var(--color-chalk)] text-ui-sans text-[13px] font-medium tracking-[0.08em] uppercase transition-colors hover:border-[var(--color-signal-lime)] hover:text-[var(--color-signal-lime)]">
              CREATE ALERT
            </button>
          </form>

          {alerts.length === 0 ? (
            <p className="text-ui-sans text-[13px] text-[var(--color-smoke)]">No active alerts.</p>
          ) : (
            <div className="space-y-[16px]">
              {alerts.map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-[24px] border border-[var(--color-graphite)] bg-[var(--surface-raised)]">
                  <div className="flex items-center gap-[24px]">
                    <div className="text-ui-sans text-[13px] text-[var(--color-chalk)] font-medium">{alert.symbol}</div>
                    <div className="text-code-mono text-[14px] text-[var(--color-smoke)]">{alert.condition}</div>
                  </div>
                  <div className="flex items-center gap-[24px]">
                    <span className="text-ui-sans text-[10px] uppercase font-bold tracking-[0.18em] border border-[var(--color-signal-lime)] text-[var(--color-signal-lime)] px-2 py-0.5">{alert.status}</span>
                    <button onClick={() => handleDeleteAlert(alert.id)} className="text-[var(--color-smoke)] hover:text-[#ff4a4a] transition-colors">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
