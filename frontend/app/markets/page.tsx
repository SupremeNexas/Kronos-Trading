'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { searchSymbols, getMarketQuote } from '@/lib/api';
import { Search, TrendingUp, TrendingDown, Clock, Activity, BarChart2 } from 'lucide-react';

const WATCHLIST_SYMBOLS = ["AAPL", "NVDA", "MSFT", "TSLA", "BTCUSD", "ETHUSD", "^NSEI", "AMZN"];

export default function MarketsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('All');
  
  const [watchlistData, setWatchlistData] = useState<any[]>([]);
  const [loadingWatchlist, setLoadingWatchlist] = useState(true);

  useEffect(() => {
    async function loadWatchlist() {
      try {
        setLoadingWatchlist(true);
        const promises = WATCHLIST_SYMBOLS.map(sym => getMarketQuote(sym));
        const results = await Promise.all(promises);
        setWatchlistData(results.map(r => r.data));
      } catch (err) {
        console.error("Failed to load watchlist quotes", err);
      } finally {
        setLoadingWatchlist(false);
      }
    }
    loadWatchlist();
  }, []);

  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchQuery.trim().length > 1) {
        setIsSearching(true);
        try {
          const res = await searchSymbols(searchQuery);
          setSearchResults(res.data.results || []);
        } catch (err) {
          console.error(err);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSearchResults([]);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const tabs = ["All", "US Equities", "Indian", "Crypto", "Commodities", "Forex"];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 pb-20">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header & Search */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Markets Overview</h1>
            <p className="text-slate-400">Search and discover financial instruments</p>
          </div>
          
          <div className="relative w-full md:w-96">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-slate-500" />
            </div>
            <input
              type="text"
              placeholder="Search symbols (e.g., AAPL, NVDA)..."
              className="block w-full pl-10 pr-3 py-3 border border-slate-700 bg-slate-900 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {isSearching && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <Activity className="h-4 w-4 text-emerald-500 animate-spin" />
              </div>
            )}
            
            {/* Search Results Dropdown */}
            {searchResults.length > 0 && searchQuery.length > 1 && (
              <div className="absolute z-10 w-full mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-xl max-h-60 overflow-y-auto hidden-scrollbar">
                {searchResults.map((res: any, idx: number) => (
                  <Link href={`/stocks/${res.symbol.toLowerCase()}`} key={idx} className="block px-4 py-3 hover:bg-slate-700 border-b border-slate-700/50 last:border-0">
                    <div className="flex justify-between items-center">
                      <div className="font-bold text-emerald-400">{res.symbol}</div>
                      <div className="text-xs px-2 py-1 bg-slate-900 rounded text-slate-400">{res.type || 'Equity'}</div>
                    </div>
                    <div className="text-sm text-slate-300 truncate">{res.name}</div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 overflow-x-auto border-b border-slate-800 pb-px hide-scrollbar">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 border-b-2 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab 
                  ? 'border-emerald-500 text-emerald-400' 
                  : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-600'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Watchlist Grid */}
        <div>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <BarChart2 size={20} className="text-blue-400"/> Popular Instruments
          </h2>
          
          {loadingWatchlist ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="animate-pulse bg-slate-900 h-28 rounded-xl border border-slate-800"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {watchlistData.map((quote) => {
                const isPos = quote.change >= 0;
                return (
                  <Link href={`/stocks/${quote.symbol.toLowerCase()}`} key={quote.symbol}>
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-slate-600 hover:bg-slate-800/80 transition-all cursor-pointer group">
                      <div className="flex justify-between items-start mb-3">
                        <div className="font-bold text-lg group-hover:text-emerald-400 transition-colors">{quote.symbol}</div>
                        <div className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          quote.data_status === 'LIVE' ? 'bg-emerald-900/40 text-emerald-400' : 'bg-slate-800 text-slate-400'
                        }`}>
                          {quote.data_status || 'DELAYED'}
                        </div>
                      </div>
                      <div className="text-2xl font-semibold mb-1">
                        ${quote.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <div className={`flex items-center font-medium ${isPos ? 'text-emerald-400' : 'text-red-400'}`}>
                          {isPos ? <TrendingUp size={14} className="mr-1" /> : <TrendingDown size={14} className="mr-1" />}
                          {isPos ? '+' : ''}{quote.change_pct}%
                        </div>
                        <div className="text-slate-500 text-xs">
                          Vol: {quote.volume ? (quote.volume / 1000000).toFixed(1) + 'M' : 'N/A'}
                        </div>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
