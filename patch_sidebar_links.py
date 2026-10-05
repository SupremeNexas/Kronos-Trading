import re

with open('frontend/components/Sidebar.tsx', 'r') as f:
    content = f.read()

new_nav = """
const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Markets", href: "/markets", icon: TrendingUp },
  { label: "Forecast", href: "/forecast", icon: Brain, badge: "AI" },
  { label: "Strategies", href: "/strategies", icon: Zap, badge: "New" },
  { label: "Terminal", href: "/terminal", icon: BarChart3 },
  { label: "Portfolio", href: "/portfolio", icon: Wallet },
  { label: "My Stocks", href: "/my-stocks", icon: Diamond },
  { label: "Trades", href: "/trades", icon: BarChart3 },
  { label: "Watchlist", href: "/watchlist", icon: Star },
  { label: "Research", href: "/research", icon: FileSearch },
  { label: "Backtest", href: "/backtest", icon: BarChart3 },
  { label: "Alerts", href: "/alerts", icon: Bell },
  { label: "Profile", href: "/profile", icon: ShieldCheck },
  { label: "Settings", href: "/settings", icon: Settings },
];
"""
content = re.sub(r'const navItems.*?\n\];', new_nav.strip(), content, flags=re.DOTALL)

# Let's also patch the user profile at the bottom of the sidebar.
user_profile = """
          <div className="flex items-center space-x-3 w-full">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0 text-blue-400 font-bold">
              {user ? user.name.charAt(0).toUpperCase() : "..."}
            </div>
            {!collapsed && (
              <div className="overflow-hidden flex-1 cursor-pointer" onClick={() => window.location.href='/profile'}>
                <p className="text-sm font-medium text-white truncate">{user ? user.name : "Loading..."}</p>
                <div className="flex items-center space-x-1 mt-0.5">
                  <ShieldCheck className="w-3 h-3 text-brand-green" />
                  <p className="text-xs font-semibold text-brand-green uppercase tracking-wide">
                    {user ? user.role : "MEMBER"}
                  </p>
                </div>
              </div>
            )}
            {!collapsed && (
              <div className="cursor-pointer text-gray-500 hover:text-white" onClick={async () => {
                await axios.post('/api/auth/logout');
                window.location.href = '/login';
              }}>
                 <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
              </div>
            )}
          </div>
"""

# Note, we need to fetch user in Sidebar via useEffect or just let a global context do it.
# To keep it simple in Sidebar:
imports = """
import React, { useState, useEffect } from "react";
import axios from "axios";
"""

content = content.replace('import React, { useState } from "react";', imports)

sidebar_hooks = """
export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
     axios.get('/api/auth/me', { withCredentials: true })
        .then(res => setUser(res.data.user))
        .catch(err => {
            if (pathname !== '/login' && pathname !== '/register') {
               window.location.href = '/login';
            }
        });
  }, [pathname]);

  const isLinkActive = (href: string) => {
"""

content = re.sub(r'export default function Sidebar\(\) \{.*?const isLinkActive = \(href: string\) => \{', sidebar_hooks.strip() + " {", content, flags=re.DOTALL)

# Replace the static profile section
content = re.sub(
    r'<div className="flex items-center space-x-3 w-full">.*?<div className="overflow-hidden">.*?</div>.*?</div>',
    user_profile.strip(),
    content,
    flags=re.DOTALL
)

with open('frontend/components/Sidebar.tsx', 'w') as f:
    f.write(content)
