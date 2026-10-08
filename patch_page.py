import re
with open("frontend/app/page.tsx", "r") as f:
    text = f.read()

# Add a client side redirect if needed in page.tsx by making it a Client Component
# Actually, we can just use `redirect` in the server side logic, because Server Components can read process.env.
server_code = """
import { redirect } from 'next/navigation';

export default function Home() {
  if (process.env.NEXT_PUBLIC_LOCAL_TRADING_MODE === 'true') {
    redirect('/dashboard');
  }
"""

text = text.replace("export default function Home() {", server_code)

with open("frontend/app/page.tsx", "w") as f:
    f.write(text)

