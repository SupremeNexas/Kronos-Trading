"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Diamond,
  LayoutDashboard,
  TrendingUp,
  Brain,
  Wallet,
  Star,
  BarChart3,
  FileSearch,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Markets", href: "/markets", icon: TrendingUp },
  { label: "Forecast", href: "/forecast", icon: Brain, badge: "AI" },
  { label: "Portfolio", href: "/portfolio", icon: Wallet },
  { label: "Watchlist", href: "/watchlist", icon: Star },
  { label: "Backtest", href: "/backtest", icon: BarChart3 },
  { label: "Research", href: "/research", icon: FileSearch },
  { label: "Alerts", href: "/alerts", icon: Bell },
  { label: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  const isLinkActive = (href: string) => {
    if (href === "/dashboard" && (pathname === "/" || pathname === "/dashboard")) {
      return true;
    }
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  return (
    <aside
      className={cn(
        "relative flex flex-col bg-slate-900 border-r border-slate-800 transition-all duration-300 ease-in-out select-none z-30 shrink-0",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Top Brand Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800/80 bg-slate-900/90 backdrop-blur">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 overflow-hidden group focus:outline-none"
        >
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-cyan-500 to-blue-500 shadow-lg shadow-cyan-500/20 text-white shrink-0 group-hover:scale-105 transition-transform duration-200">
            <Diamond className="w-5 h-5 text-slate-950 fill-cyan-100" />
          </div>
          {!collapsed && (
            <div className="flex flex-col min-w-0 transition-opacity duration-200">
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg tracking-tight text-white">
                  KRONOS
                </span>
                <span className="px-1.5 py-0.2 text-[10px] font-semibold uppercase tracking-wider rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  AI
                </span>
              </div>
              <span className="text-[11px] font-medium text-slate-400 truncate tracking-tight">
                AI-Powered Market Intelligence
              </span>
            </div>
          )}
        </Link>

        {/* Collapse Button */}
        <button
          type="button"
          onClick={() => setCollapsed(!collapsed)}
          className="hidden md:flex items-center justify-center w-7 h-7 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors border border-slate-800 focus:outline-none"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 py-4 px-3 space-y-1.5 overflow-y-auto overflow-x-hidden">
        <div className={cn("px-3 mb-2", collapsed && "text-center px-0")}>
          {!collapsed ? (
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              Platform Navigation
            </span>
          ) : (
            <div className="w-4 h-0.5 bg-slate-800 mx-auto rounded-full" />
          )}
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isLinkActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.label : undefined}
              className={cn(
                "group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                active
                  ? "bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-400 shadow-[inset_0_1px_0_0_rgba(6,182,212,0.1)] font-semibold"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 border-l-2 border-transparent",
                collapsed && "justify-center px-0"
              )}
            >
              <Icon
                className={cn(
                  "w-5 h-5 shrink-0 transition-colors",
                  active
                    ? "text-cyan-400"
                    : "text-slate-400 group-hover:text-slate-200"
                )}
              />

              {!collapsed && (
                <div className="flex items-center justify-between flex-1 truncate">
                  <span className="truncate">{item.label}</span>
                  {item.badge && (
                    <span className="flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/30">
                      <Sparkles className="w-2.5 h-2.5" />
                      {item.badge}
                    </span>
                  )}
                </div>
              )}

              {/* Collapsed Tooltip Floating Indicator */}
              {collapsed && (
                <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-slate-900 text-slate-100 text-xs rounded-md shadow-xl border border-slate-700 whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50">
                  {item.label}
                  {item.badge && (
                    <span className="ml-1.5 text-[9px] px-1 py-0.2 rounded bg-cyan-500/20 text-cyan-300">
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </Link>
          );
        })}
      </div>

      {/* Bottom User & Mode Section */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/60 space-y-3">
        {/* Demo Mode Badge */}
        {!collapsed ? (
          <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-400">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-semibold uppercase tracking-wider">
                Demo Mode
              </span>
            </div>
            <ShieldCheck className="w-4 h-4 text-emerald-400/80" />
          </div>
        ) : (
          <div
            className="flex justify-center py-2"
            title="Demo Mode: Paper Trading Active"
          >
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
          </div>
        )}

        {/* User Profile Card */}
        <div
          className={cn(
            "flex items-center gap-3 p-2 rounded-lg bg-slate-800/40 border border-slate-800 hover:bg-slate-800/70 transition-colors cursor-pointer",
            collapsed && "justify-center p-1.5"
          )}
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-white shadow-sm shrink-0">
            KP
          </div>

          {!collapsed && (
            <div className="flex flex-col min-w-0 flex-1">
              <span className="text-xs font-semibold text-slate-200 truncate">
                Kronos Pro Trader
              </span>
              <span className="text-[10px] text-slate-400 truncate">
                Quant Strategy Desk
              </span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
