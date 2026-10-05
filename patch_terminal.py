with open("frontend/app/terminal/page.tsx", "r") as f:
    content = f.read()

# Fix the placement
content = content.replace("""  const searchParams = useSearchParams();
  const initSymbol = searchParams?.get('symbol') || '';
  const strategyParam = searchParams?.get('strategy') || '';
  const scanIdParam = searchParams?.get('scan_id') || '';
  const scoreParam = searchParams?.get('score') || '';
  const volParam = searchParams?.get('vol') || '';
  const attentionParam = searchParams?.get('attention') || '';
  const momentumParam = searchParams?.get('momentum') || '';
  
  useEffect(() => {
    if (initSymbol && !symbol) {
      setSymbol(initSymbol);
      fetchSymbolData(initSymbol);
    }
  }, [initSymbol]);
""", "")

idx = content.find("const [limitPrice, setLimitPrice] = useState(0);")
insert_idx = content.find("\n", idx) + 1

new_vars = """
  const searchParams = useSearchParams();
  const initSymbol = searchParams?.get('symbol') || '';
  const strategyParam = searchParams?.get('strategy') || '';
  const scanIdParam = searchParams?.get('scan_id') || '';
  const scoreParam = searchParams?.get('score') || '';
  const volParam = searchParams?.get('vol') || '';
  const attentionParam = searchParams?.get('attention') || '';
  const momentumParam = searchParams?.get('momentum') || '';
  
  useEffect(() => {
    if (initSymbol && !symbol) {
      setSymbol(initSymbol.toUpperCase());
      fetchSymbolData(initSymbol.toUpperCase());
    }
  }, [initSymbol]);
"""

content = content[:insert_idx] + new_vars + content[insert_idx:]

# Next.js 13+ requires useSearchParams to be wrapped in a suspense boundary ideally, but I can also wrap the whole page if needed.
# Let's see if we get an issue. To be safe, we rename ManualTradingTerminal to ManualTradingTerminalInner and export default function ManualTradingTerminal() { return <Suspense><ManualTradingTerminalInner/></Suspense> }

content = content.replace("export default function ManualTradingTerminal() {", "function ManualTradingTerminalInner() {")

suspense_wrapper = """
import { Suspense } from 'react';

export default function ManualTradingTerminal() {
  return (
    <Suspense fallback={<div>Loading terminal...</div>}>
      <ManualTradingTerminalInner />
    </Suspense>
  );
}
"""
content = content + suspense_wrapper

with open("frontend/app/terminal/page.tsx", "w") as f:
    f.write(content)
print("Fixed terminal patching")
