"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Bell,
  User,
  Activity,
  Command,
  ChevronDown,
  TrendingUp,
  Sparkles,
  ExternalLink,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface HeaderProps {
  onMobileMenuToggle?: () => void;
}

export default function Header({ onMobileMenuToggle }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const router = useRouter();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const cleanSymbol = searchQuery.trim().toUpperCase();
    router.push(`/forecast?symbol=${encodeURIComponent(cleanSymbol)}`);
  };

  // Quick ticker presets
  const marketTickers = [
    { name: "S&P 500", val: "5,864.67", chg: "+0.42%", positive: true },
    { name: "NASDAQ", val: "18,518.61", chg: "+0.83%", positive: true },
    { name: "SSE Index", val: "3,370.20", chg: "+0.31%", positive: true },
    { name: "BTC/USD", val: "$92,450", chg: "-0.65%", positive: false },
  ];

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-slate-800/80 bg-slate-950/80 px-4 md:px-6 backdrop-blur-md">
      {/* Left: Mobile Toggle & Quick Search */}
      <div className="flex items-center gap-3 md:gap-4 flex-1 max-w-xl">
        {onMobileMenuToggle && (
          <button
            type="button"
            onClick={onMobileMenuToggle}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-900 border border-slate-800"
            aria-label="Toggle mobile menu"
          >
            <span className="sr-only">Open main menu</span>
            <div className="w-5 h-4 flex flex-col justify-between">
              <span className="w-full h-0.5 bg-current rounded-full" />
              <span className="w-full h-0.5 bg-current rounded-full" />
              <span className="w-full h-0.5 bg-current rounded-full" />
            </div>
          </button>
        )}

        {/* Search Bar */}
        <form
          onSubmit={handleSearchSubmit}
          className="relative w-full flex items-center group"
        >
          <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-cyan-400 transition-colors">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search symbol (e.g. AAPL, NVDA, TSLA, 600519)..."
            className="w-full h-10 pl-10 pr-16 text-xs sm:text-sm bg-slate-900/90 border border-slate-800 rounded-xl text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
          />
          <div className="absolute right-2.5 hidden sm:flex items-center gap-1 px-1.5 py-0.5 bg-slate-800/80 border border-slate-700/60 rounded text-[10px] font-mono text-slate-400">
            <Command className="w-3 h-3" />
            <span>K</span>
          </div>
        </form>
      </div>

      {/* Middle: Live Market Status & mini ticker pills (hidden on small mobile) */}
      <div className="hidden xl:flex items-center gap-4 px-4">
        <div className="flex items-center gap-3 text-xs border-x border-slate-800/80 px-4">
          {marketTickers.map((ticker) => (
            <div
              key={ticker.name}
              className="flex items-center gap-1.5 whitespace-nowrap"
            >
              <span className="text-slate-400 font-medium">{ticker.name}</span>
              <span className="font-semibold text-slate-200 tabular-nums">
                {ticker.val}
              </span>
              <span
                className={cn(
                  "text-[11px] font-semibold tabular-nums",
                  ticker.positive ? "text-emerald-400" : "text-rose-400"
                )}
              >
                {ticker.chg}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Market Status Pill & Quick Action Icons */}
      <div className="flex items-center gap-2.5 sm:gap-3 shrink-0 ml-3">
        {/* Market Status Live Pill */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300 shadow-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-medium text-[11px] tracking-tight">
            Markets Open
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-[10px] text-cyan-400 font-mono font-medium">
            AI Active
          </span>
        </div>

        {/* Notifications Button & Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 border border-slate-800/80 focus:outline-none transition-colors"
            aria-label="View notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-slate-950 animate-pulse" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-3 z-50 animate-in fade-in zoom-in-95">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
                <span className="text-xs font-semibold text-slate-200">
                  Real-Time AI Signals
                </span>
                <span className="text-[10px] text-cyan-400 hover:underline cursor-pointer">
                  Mark all read
                </span>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto text-xs">
                <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800 transition-colors">
                  <div className="flex items-center justify-between text-slate-300 font-semibold mb-1">
                    <span className="text-emerald-400 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> NVDA Bullish Wave
                    </span>
                    <span className="text-[10px] text-slate-500">2m ago</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Kronos autoregressive model detected high-momentum breakout
                    continuation (+3.4% horizon target).
                  </p>
                </div>
                <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800 transition-colors">
                  <div className="flex items-center justify-between text-slate-300 font-semibold mb-1">
                    <span className="text-cyan-400 flex items-center gap-1">
                      <Activity className="w-3 h-3" /> Model Sync
                    </span>
                    <span className="text-[10px] text-slate-500">14m ago</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Kronos-Base tokenizer and predictor loaded in GPU inference
                    cache.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Menu */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-1.5 sm:px-2 sm:py-1.5 rounded-xl bg-slate-900 border border-slate-800/80 hover:border-slate-700 text-slate-200 transition-colors focus:outline-none"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-white shadow-sm">
              KP
            </div>
            <span className="hidden md:inline text-xs font-semibold text-slate-200">
              Pro Desk
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden sm:inline" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50 text-xs animate-in fade-in zoom-in-95">
              <div className="px-3 py-2 border-b border-slate-800 mb-1">
                <p className="font-semibold text-slate-100">Kronos Pro Trader</p>
                <p className="text-[11px] text-slate-400">pro@kronos.quant</p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setShowUserMenu(false);
                  router.push("/portfolio");
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 flex items-center justify-between"
              >
                <span>Portfolio & Orders</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowUserMenu(false);
                  router.push("/settings");
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 flex items-center justify-between"
              >
                <span>API & Model Keys</span>
              </button>
              <div className="border-t border-slate-800 my-1" />
              <div className="px-3 py-1.5 flex items-center justify-between text-[11px] text-emerald-400">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3 h-3" /> System Nominal
                </span>
                <span className="text-slate-500 font-mono">v1.2.0</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
