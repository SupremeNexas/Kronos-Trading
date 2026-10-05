"use client";

import React, { useState, useEffect } from "react";
import { Zap, Play, CheckCircle2, History, AlertCircle, RefreshCw, Layers, Star } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

export default function SignalScannerPage() {
  const [scanHistory, setScanHistory] = useState<any[]>([]);
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [assetsToScan, setAssetsToScan] = useState("bitcoin,ethereum");
  const [mentionsStr, setMentionsStr] = useState("");
  const [scanning, setScanning] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("scanner");

  const loadData = async () => {
    setFetchLoading(true);
    try {
      const histRes = await fetch("/api/scanner/history");
      if (histRes.ok) {
        setScanHistory(await histRes.json());
      }
      const wlRes = await fetch("/api/scanner/watchlist");
      if (wlRes.ok) setWatchlist(await wlRes.json());
    } catch (e) {
      console.error(e);
    }
    setFetchLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleScan = async () => {
    const assets = assetsToScan.split(",").map(a => a.trim()).filter(a => a);
    if (assets.length === 0) return;
    
    // Parse mentions (format: "bitcoin=4,ethereum=2")
    const manualMentions: any = {};
    if (mentionsStr) {
      const parts = mentionsStr.split(",");
      for (const part of parts) {
        const [asset, count] = part.split("=");
        if (asset && count) {
          manualMentions[asset.trim()] = parseInt(count.trim(), 10) || 0;
        }
      }
    }
    
    setScanning(true);
    try {
      const res = await fetch("/api/scanner/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assets,
          manual_mentions: manualMentions
        })
      });
      if (res.ok) {
        await loadData();
      }
    } catch (e) {
      console.error(e);
    }
    setScanning(false);
  };

  return (
    <div className="flex-1 w-full bg-slate-950 p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Zap className="w-6 h-6 text-yellow-400" />
            Crypto Early-Signal Scanner
          </h1>
          <p className="text-slate-400 mt-1">
            Independent strategy module based on SebAI framework.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-slate-300">
          <Layers className="w-3.5 h-3.5 text-cyan-500" />
          <span>Status: Active</span>
          <span className="mx-2 px-1.5 py-0.5 bg-slate-800 rounded border border-slate-700">v1.0</span>
          <span>Source: CoinGecko V3</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 border-b border-slate-800 mb-6">
        <button
          onClick={() => setActiveTab("scanner")}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === "scanner"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
          )}
        >
          Scanner
        </button>
        <button
          onClick={() => setActiveTab("watchlist")}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-2",
            activeTab === "watchlist"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
          )}
        >
          Research Watchlist
          {watchlist.length > 0 && (
            <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded text-xs">
              {watchlist.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === "history"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
          )}
        >
          Past Scans
        </button>
        
        <button
          onClick={() => setActiveTab("performance")}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === "performance"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
          )}
        >
          Performance (Coming Soon)
        </button>
      </div>

      {activeTab === "scanner" && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-white font-medium mb-4 flex items-center gap-2">
              <Play className="w-4 h-4 text-cyan-400" />
              New Scan
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Assets (CoinGecko IDs, comma separated)</label>
                <input
                  type="text"
                  value={assetsToScan}
                  onChange={(e) => setAssetsToScan(e.target.value)}
                  placeholder="e.g. bitcoin, ethereum, solana"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500"
                />
              </div>
              
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Manual Mentions (Optional, format: id=count)</label>
                <input
                  type="text"
                  value={mentionsStr}
                  onChange={(e) => setMentionsStr(e.target.value)}
                  placeholder="e.g. solana=4, dogecoin=2"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500"
                />
              </div>
              
              <button
                onClick={handleScan}
                disabled={scanning}
                className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded font-medium text-sm transition-colors disabled:opacity-50"
              >
                {scanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {scanning ? "Scanning..." : "Run Scanner"}
              </button>
            </div>
            
            <div className="mt-4 p-3 bg-blue-950/30 border border-blue-900/50 rounded flex gap-3 text-sm text-blue-200">
              <AlertCircle className="w-5 h-5 shrink-0 text-blue-400" />
              <p>
                <strong>Evaluation Criteria:</strong> 1 point for Volume Ratio &ge; 1.5, 1 point for Attention (Trending or Mentions &ge; 3), 1 point for Momentum &ge; 5%. 
                Total 3/3 requires ADD TO WATCHLIST. The scanner does <strong>not</strong> produce price predictions or execute automatic trades.
              </p>
            </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-white font-medium mb-4 flex items-center gap-2">
              <History className="w-4 h-4 text-cyan-400" />
              Latest Results
            </h3>
            
            <ScanResultsTable results={scanHistory.slice(-10).reverse()} />
          </div>
        </div>
      )}

      {activeTab === "watchlist" && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-yellow-400 font-medium mb-4 flex items-center gap-2">
              <Star className="w-4 h-4" />
              Research Watchlist
            </h3>
            
            {watchlist.length === 0 ? (
              <p className="text-slate-400 text-sm">No assets in watchlist yet. Run the scanner to discover signals.</p>
            ) : (
              <ScanResultsTable results={watchlist} />
            )}
          </div>
        </div>
      )}
      
      {activeTab === "history" && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <h3 className="text-white font-medium mb-4">Complete Scan History</h3>
          <ScanResultsTable results={scanHistory.slice().reverse()} />
        </div>
      )}

      {activeTab === "performance" && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <h3 className="text-white font-medium mb-4">Strategy Performance (Coming Soon)</h3>
          <p className="text-slate-400 text-sm mb-4">
            Compare KRONOS strategy performance vs EARLY_SIGNAL_SCANNER performance vs user decisions.
            This area will display matched performance metrics once manual trades have been executed based on scanner signals.
          </p>
          <div className="border border-slate-800 rounded bg-slate-950 flex p-8 items-center justify-center text-slate-500">
            Metrics processing pipeline under construction. (Coming Soon)
          </div>
        </div>
      )}

    </div>
  );
}

function ScanResultsTable({ results }: { results: any[] }) {
  if (!results || results.length === 0) {
    return <p className="text-slate-500 text-sm">No scans available.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-slate-400 bg-slate-950/50 uppercase">
          <tr>
            <th className="px-4 py-3 rounded-tl-lg">Timestamp</th>
            <th className="px-4 py-3">Asset</th>
            <th className="px-4 py-3">Vol Ratio</th>
            <th className="px-4 py-3">Attention</th>
            <th className="px-4 py-3">Momentum</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Decision</th>
            <th className="px-4 py-3 rounded-tr-lg">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {results.map((res, idx) => (
            <React.Fragment key={res.signal_scan_id + idx}>
              <tr className="hover:bg-slate-800/20 text-slate-300 group">
                <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-500">
                  {new Date(res.timestamp).toLocaleString()}
                </td>
                <td className="px-4 py-3 font-medium text-white capitalize">
                  {res.asset}
                </td>
                <td className="px-4 py-3">
                  {typeof res.volume_ratio === "number" ? res.volume_ratio.toFixed(2) : res.volume_ratio}
                </td>
                <td className="px-4 py-3">{res.attention_score}</td>
                <td className="px-4 py-3">
                  {typeof res.momentum_7d === "number" ? (
                    <span className={res.momentum_7d > 0 ? "text-emerald-400" : "text-rose-400"}>
                      {res.momentum_7d > 0 ? "+" : ""}{res.momentum_7d.toFixed(2)}%
                    </span>
                  ) : res.momentum_7d}
                </td>
                <td className="px-4 py-3 font-bold text-center">
                  <span className={cn(
                    "inline-block px-2 py-0.5 rounded text-xs",
                    res.score === 3 ? "bg-emerald-500/20 text-emerald-400" :
                    res.score === 2 ? "bg-yellow-500/20 text-yellow-400" : "bg-slate-800 text-slate-400"
                  )}>
                    {res.score}/3
                  </span>
                </td>
                <td className="px-4 py-3">
                  {res.decision === "WATCHLIST" ? (
                    <span className="text-yellow-400 font-bold flex items-center gap-1 text-xs">
                      <Star className="w-3 h-3 fill-yellow-400" />
                      WATCHLIST
                    </span>
                  ) : (
                    <span className="text-slate-400 text-xs">MONITOR</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <Link 
                    href={`/terminal?symbol=${res.asset.toUpperCase()}&strategy=EARLY_SIGNAL_SCANNER&scan_id=${res.signal_scan_id}&score=${res.score}&vol=${typeof res.volume_ratio === 'number' ? res.volume_ratio.toFixed(4) : ''}&attention=${res.attention_score}&momentum=${typeof res.momentum_7d === 'number' ? res.momentum_7d.toFixed(4) : ''}`}
                    className="px-2 py-1 bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-400 rounded text-xs font-semibold whitespace-nowrap transition-colors"
                  >
                    Open in Terminal
                  </Link>
                </td>
              </tr>
              <tr className="bg-slate-950/20 text-xs text-slate-500">
                <td colSpan={8} className="px-4 py-2 border-b border-slate-800/10">
                  <div className="flex gap-4 opacity-50 group-hover:opacity-100 transition-opacity">
                    <div><strong>Data Source:</strong> {res.data_source}</div>
                    <div className="flex-1">
                      <strong>Reasons:</strong> {res.reasons ? res.reasons.join(" | ") : "None"}
                    </div>
                  </div>
                </td>
              </tr>
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

