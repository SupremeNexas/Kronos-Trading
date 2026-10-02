'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { searchSymbols, getMarketQuote } from '@/lib/api';

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
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[40px]">

        {/* Header Options */}
        <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[24px] flex flex-col sm:flex-row gap-[16px] justify-between items-end relative">
           <div className="flex flex-col gap-2 w-full max-w-sm">
             <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">
               SEARCH MARKETS
             </label>
             <input
               type="text"
               value={searchQuery}
               onChange={(e) => setSearchQuery(e.target.value)}
               placeholder="AAPL, NVDA..."
               className="bg-transparent border border-[var(--color-slate)] p-2 text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none uppercase"
             />
           </div>

           {/* Search Results Dropdown */}
           {searchResults.length > 0 && searchQuery.length > 1 && (
             <div className="absolute top-[80px] left-[24px] z-10 w-full max-w-sm bg-[var(--surface-raised)] border border-[var(--color-graphite)] shadow-xl max-h-60 overflow-y-auto">
               {searchResults.map((res: any, idx: number) => (
                 <Link href={`/stocks/${res.symbol.toLowerCase()}`} key={idx} className="block p-4 border-b border-[var(--color-graphite)] hover:bg-[var(--surface-hover)] last:border-0 transition-colors">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-ui-sans text-[13px] font-medium text-[var(--color-chalk)]">{res.symbol}</span>
                     <span className="text-ui-sans text-[10px] uppercase font-medium tracking-[0.18em] border border-[var(--color-slate)] px-2 py-0.5 text-[var(--color-smoke)]">{res.type || 'Equity'}</span>
                   </div>
                   <div className="text-ui-sans text-[11px] text-[var(--color-ash)] truncate">{res.name}</div>
                 </Link>
               ))}
             </div>
           )}
        </div>

        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ POPULAR INSTRUMENTS ]
          </div>

          <div className="flex space-x-8 border-b border-[var(--color-graphite)] pb-[12px] mb-[40px] overflow-x-auto hide-scrollbar">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`text-ui-sans text-[11px] uppercase tracking-[0.18em] whitespace-nowrap transition-colors ${
                  activeTab === tab
                    ? 'text-[var(--color-signal-lime)] font-bold'
                    : 'text-[var(--color-smoke)] hover:text-[var(--color-chalk)]'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {loadingWatchlist ? (
            <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[var(--color-smoke)] uppercase">Loading markets...</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-[20px]">
              {watchlistData.map((quote) => {
                const isPos = quote.change >= 0;
                return (
                  <Link href={`/stocks/${quote.symbol.toLowerCase()}`} key={quote.symbol}>
                    <div className="bg-[var(--surface-raised)] border border-[var(--color-graphite)] p-[24px] hover:border-[var(--color-slate)] hover:bg-[var(--surface-hover)] transition-all flex flex-col justify-between group h-full cursor-pointer">
                      <div className="flex justify-between items-start mb-6">
                        <span className="text-ui-sans text-[13px] font-medium text-[var(--color-chalk)]">{quote.symbol}</span>
                        <span className="text-ui-sans text-[10px] uppercase font-medium tracking-[0.18em] text-[var(--color-smoke)]">
                           {quote.data_status || 'DELAYED'}
                        </span>
                      </div>
                      <div>
                        <div className="text-code-mono text-[24px] font-normal text-[var(--color-chalk)] leading-none mb-2">
                           ${quote.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                        <div className="flex justify-between items-end">
                           <div className={`text-code-mono text-[11px] font-normal ${isPos ? 'text-[var(--color-signal-lime)]' : 'text-[var(--color-ash)]'}`}>
                             {isPos ? '+' : ''}{quote.change_pct}%
                           </div>
                           <div className="text-ui-sans text-[11px] text-[var(--color-ash)]">
                             Vol: {quote.volume ? (quote.volume / 1000000).toFixed(1) + 'M' : 'N/A'}
                           </div>
                        </div>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}