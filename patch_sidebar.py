
import re

with open('frontend/components/Sidebar.tsx', 'r') as f:
    text = f.read()

nav_old = '''const TOP_NAV_ITEMS: NavItem[] = [
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
];'''

nav_new = '''const TOP_NAV_ITEMS: NavItem[] = [
  { label: "Trade Stock", href: "/terminal", icon: Zap, badge: "Terminal" },
  { label: "My Trades", href: "/trades", icon: BarChart3 },
  { label: "Tactic Performance", href: "/tactics", icon: LayoutDashboard },
  { label: "Portfolio", href: "/portfolio", icon: Wallet },
  { label: "Markets", href: "/markets", icon: TrendingUp },
  { label: "Forecast", href: "/forecast", icon: Brain, badge: "AI" },
  { label: "Scanner", href: "/strategies", icon: Zap },
  { label: "Watchlist", href: "/watchlist", icon: Star },
  { label: "Research", href: "/research", icon: FileSearch },
];'''

text = text.replace(nav_old, nav_new)
with open('frontend/components/Sidebar.tsx', 'w') as f:
    f.write(text)
