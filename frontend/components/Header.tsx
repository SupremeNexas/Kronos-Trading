"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "DASHBOARD", href: "/dashboard" },
  { label: "MARKETS", href: "/markets" },
  { label: "FORECAST", href: "/forecast" },
  { label: "STRATEGIES", href: "/strategies" },
  { label: "TERMINAL", href: "/terminal" },
  { label: "PORTFOLIO", href: "/portfolio" },
  { label: "MY STOCKS", href: "/my-stocks" },
  { label: "TRADES", href: "/trades" },
  { label: "WATCHLIST", href: "/watchlist" },
  { label: "RESEARCH", href: "/research" },
  { label: "BACKTEST", href: "/backtest" },
  { label: "ALERTS", href: "/alerts" },
  { label: "VERIFICATION", href: "/verification" }
];

export default function Header() {
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Exclude auth routes from automatic redirect
    const isAuthRoute = pathname === '/login' || pathname === '/register' || pathname === '/';
    axios.get('/api/auth/me', { withCredentials: true })
      .then(res => setUser(res.data.user))
      .catch(err => {
        if (!isAuthRoute) window.location.href = '/login';
      });
  }, [pathname]);

  return (
    <header className="sticky top-0 z-50 w-full flex justify-center bg-[var(--color-void-black)] border-b border-[var(--color-graphite)] h-[64px]">
      <div className="flex w-full max-w-[var(--layout-page-max-width)] items-center justify-between px-4 md:px-8">

        {/* Left: Wordmark */}
        <Link
          href="/"
          className="text-display-serif font-light text-[20px] tracking-[-0.01em] text-[var(--color-chalk)]"
        >
          KRONOS
        </Link>

        {/* Center: Nav Items */}
        <nav className="hidden lg:flex items-center gap-[32px]">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "text-ui-sans text-[13px] font-medium tracking-[0.18em] transition-colors",
                  isActive
                    ? "text-[var(--color-signal-lime)]"
                    : "text-[var(--color-chalk)] hover:text-[var(--color-signal-lime)]"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Right: CTA */}
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <Link href="/profile" className="flex items-center space-x-2 text-ui-sans tracking-[0.08em] hover:text-[var(--color-signal-lime)] text-[var(--color-chalk)]">
                 <div className="w-8 h-8 rounded-full bg-[var(--color-signal-lime)]/20 border border-[var(--color-signal-lime)]/50 flex items-center justify-center text-[var(--color-signal-lime)] font-bold text-sm">
                   {user.name.charAt(0).toUpperCase()}
                 </div>
                 <span className="text-[12px] font-medium hidden md:block">{user.name.toUpperCase()}</span>
                 <span className="text-[10px] text-[var(--color-ash)] uppercase hidden lg:block border border-[var(--color-graphite)] px-1">{user.role}</span>
              </Link>
              <button onClick={async () => { await axios.post('/api/auth/logout', {}, { withCredentials: true }); window.location.href='/login'; }}
                className="text-[11px] text-[var(--color-ash)] hover:text-white border-l border-[var(--color-graphite)] pl-4">
                LOGOUT
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="text-ui-sans text-[13px] font-medium tracking-[0.08em] px-[20px] py-[10px] rounded-[4px] border border-[var(--color-signal-lime)] text-[var(--color-signal-lime)] bg-transparent glow-signal active:scale-95 transition-all"
            >
              LOGIN
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}