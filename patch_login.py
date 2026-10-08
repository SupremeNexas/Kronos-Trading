import os 
for page in ["frontend/app/login/page.tsx", "frontend/app/register/page.tsx"]:
    with open(page, "r") as f:
        text = f.read()

    # The login page is a client component ('use client'). So we can just put a useEffect or window.location.
    # Actually, we already have it in Header? No, Header excludes isAuthRoute.
    if 'use client' in text:
        add = """
  React.useEffect(() => {
    if (process.env.NEXT_PUBLIC_LOCAL_TRADING_MODE === 'true') {
      window.location.href = '/dashboard';
    }
  }, []);
"""
        # Find exactly where to place it
        if "export default function" in text:
            # find first '{' after export default function
            idx = text.find("{", text.find("export default function"))
            if idx != -1:
                text = text[:idx+1] + add + text[idx+1:]
        
    with open(page, "w") as f:
        f.write(text)

