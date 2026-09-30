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
import { cn } from '@/lib/utils';

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

  if (loading) return <div className="flex h-screen items-center justify-center text-slate-50"><Loader2 className="animate-spin h-8 w-8" /></div>;

  return (
    <div className="p-6 space-y-8 bg-slate-950 min-h-screen text-slate-50">
      <h1 className="text-3xl font-bold flex items-center gap-3">
        <Star className="text-primary" /> Watchlist & Alerts
      </h1>

      {/* Watchlist Section */}
      <section className="fintech-card p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold flex items-center gap-2"><Star className="w-5 h-5 text-yellow-500" /> Watchlist</h2>
          <form onSubmit={handleAddWatchlist} className="flex gap-2">
            <input
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              placeholder="Symbol (e.g. AAPL)"
              className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 focus:ring-1 focus:ring-primary outline-none"
            />
            <button className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2">
              <Plus className="w-4 h-4" /> Add
            </button>
          </form>
        </div>

        {watchlist.length === 0 ? (
          <p className="text-slate-500 italic">Your watchlist is empty. Add symbols to track.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {watchlist.map((item) => (
              <div key={item.symbol} className="fintech-card p-4 border border-slate-800 flex justify-between items-center">
                <div>
                  <div className="font-bold text-lg">{item.symbol}</div>
                  <div className="text-sm text-slate-400">{item.name}</div>
                </div>
                <div className="text-right">
                  {item.quote ? (
                    <>
                      <div className="font-mono text-lg">${item.quote.price.toFixed(2)}</div>
                      <div className={cn("text-sm", item.quote.change >= 0 ? "text-emerald-500" : "text-rose-500")}>
                        {item.quote.change > 0 ? '+' : ''}{item.quote.change.toFixed(2)} ({item.quote.change_pct.toFixed(2)}%)
                      </div>
                    </>
                  ) : <div className="text-slate-600">N/A</div>}
                </div>
                <button onClick={() => handleRemoveWatchlist(item.symbol)} className="text-slate-500 hover:text-rose-500">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Alerts Section */}
      <section className="fintech-card p-6">
        <h2 className="text-xl font-semibold flex items-center gap-2 mb-6"><Bell className="w-5 h-5 text-primary" /> Price Alerts</h2>

        <form onSubmit={handleCreateAlert} className="flex flex-wrap gap-4 mb-6 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
          <input
            value={newAlertSymbol}
            onChange={(e) => setNewAlertSymbol(e.target.value)}
            placeholder="Symbol"
            className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 outline-none"
          />
          <select
            value={newAlertType}
            onChange={(e) => setNewAlertType(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 outline-none"
          >
            <option value="PRICE_ABOVE">Price Above</option>
            <option value="PRICE_BELOW">Price Below</option>
          </select>
          <input
            type="number"
            value={newTargetPrice}
            onChange={(e) => setNewTargetPrice(e.target.value)}
            placeholder="Target Price"
            className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 outline-none"
          />
          <button className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg font-medium">Create Alert</button>
        </form>

        {alerts.length === 0 ? (
          <p className="text-slate-500 italic">No active alerts.</p>
        ) : (
          <div className="space-y-2">
            {alerts.map((alert) => (
              <div key={alert.id} className="fintech-card flex items-center justify-between p-4 border border-slate-800">
                <div className="flex items-center gap-4">
                  <AlertCircle className="text-primary w-5 h-5" />
                  <div>
                    <span className="font-bold">{alert.symbol}</span>
                    <span className="text-slate-400 ml-2">{alert.condition}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 rounded-full text-xs font-semibold">{alert.status}</span>
                  <button onClick={() => handleDeleteAlert(alert.id)} className="text-slate-500 hover:text-rose-500">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
