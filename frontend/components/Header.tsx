"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "MARKETS", href: "/markets" },
  { label: "ANALYSIS", href: "/analysis" },
  { label: "PREDICTIONS", href: "/forecast" },
  { label: "PORTFOLIO", href: "/portfolio" },
  { label: "PAPER TRADING", href: "/paper-trading" },
  { label: "RISK", href: "/risk" },
  { label: "RESEARCH", href: "/research" },
];

export default function Header() {
  const pathname = usePathname();

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
        <div className="flex items-center">
          <Link
            href="/paper-trading"
            className="text-ui-sans text-[13px] font-medium tracking-[0.08em] px-[20px] py-[10px] rounded-[4px] border border-[var(--color-signal-lime)] text-[var(--color-signal-lime)] bg-transparent glow-signal active:scale-95 transition-all"
          >
            PAPER ACCOUNT
          </Link>
        </div>

      </div>
    </header>
  );
}