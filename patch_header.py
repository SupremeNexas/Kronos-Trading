with open("frontend/components/Header.tsx", "r") as f:
    content = f.read()

import re

# In useEffect, if NEXT_PUBLIC_LOCAL_TRADING_MODE we might stay on the page. But if local mode is true, get_current_user returns the dummy user anyway!
# However, for '/' we might want to redirect to '/dashboard' if local mode is true.

content = content.replace("const isAuthRoute = pathname === '/login' || pathname === '/register' || pathname === '/';",
"""const isAuthRoute = pathname === '/login' || pathname === '/register' || pathname === '/';
    const isLocalMode = process.env.NEXT_PUBLIC_LOCAL_TRADING_MODE === 'true';
    if (isLocalMode && isAuthRoute && pathname !== '/dashboard') {
        window.location.href = '/dashboard';
        return;
    }""")

with open("frontend/components/Header.tsx", "w") as f:
    f.write(content)

