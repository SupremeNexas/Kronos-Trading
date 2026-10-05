import re

with open('frontend/components/Header.tsx', 'r') as f:
    content = f.read()

new_nav = """
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
  { label: "ALERTS", href: "/alerts" }
];
"""
content = re.sub(r'const NAV_ITEMS = \[.*?\];', new_nav.strip(), content, flags=re.DOTALL)

# Add axios import, useState, useEffect to Header
if "import axios from" not in content:
    content = content.replace('import React from "react";', 'import React, { useState, useEffect } from "react";\nimport axios from "axios";')

# Inject user state in Header 
hook_injection = """
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
"""
content = re.sub(r'export default function Header\(\) \{\n.*?const pathname = usePathname\(\);', hook_injection.strip(), content, flags=re.DOTALL)

cta_replacement = """
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
              <button onClick={async () => { await axios.post('/api/auth/logout'); window.location.href='/login'; }}
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
"""
content = re.sub(r'\{/\* Right: CTA \*/\}.*?</header>', cta_replacement.strip() + "\n      </div>\n    </header>", content, flags=re.DOTALL)

with open('frontend/components/Header.tsx', 'w') as f:
    f.write(content)

