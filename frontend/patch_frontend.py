with open('/Users/supryo/Desktop/Kronos-master/frontend/app/paper-trading/page.tsx', 'r') as f:
    text = f.read()

# Add TRADE LEDGER to tabs
text = text.replace("'DASHBOARD', 'PREDICTION LEDGER', 'TRADE OUTCOMES', 'MODEL SCORECARD'", 
                   "'DASHBOARD', 'PREDICTION LEDGER', 'TRADE OUTCOMES', 'TRADE LEDGER', 'MODEL SCORECARD'")

# Add Trade Ledger state & fetching
insert_state = """
  const [trades, setTrades] = useState<any[]>([]);

  const fetchTrades = async () => {
    try {
      const res = await axios.get('/api/lab/trade-ledger');
      setTrades(res.data.data || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);
"""
text = text.replace("fetchAccuracy();\n  }, []);", "fetchAccuracy();\n    fetchTrades();\n  }, []);" + insert_state)

# Add Trade Ledger view
ledger_view = """
        {activeTab === 'TRADE LEDGER' && (
          <div className="space-y-4">
             <div className="text-ui-sans text-[12px] text-[var(--color-ash)]">
                Record of every paper-trading proposal and actual Alpaca paper order.
             </div>
             <div className="overflow-x-auto border border-[var(--color-graphite)] text-code-mono text-[12px] bg-[var(--surface-card)]">
               <table className="w-full text-left">
                  <thead className="bg-[#1a1a1a] border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                    <tr>
                      <th className="p-3">TIME</th>
                      <th className="p-3">SYMBOL</th>
                      <th className="p-3">SIDE</th>
                      <th className="p-3">QTY (PROP/ACT)</th>
                      <th className="p-3">TYPE</th>
                      <th className="p-3">PRICE</th>
                      <th className="p-3">ALPACA ID</th>
                      <th className="p-3">STATUS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.map((t, i) => (
                      <tr key={i} className="border-b border-[var(--color-graphite)] hover:bg-[#222]">
                        <td className="p-3">{new Date(t.created_at).toLocaleString()}</td>
                        <td className="p-3">{t.symbol}</td>
                        <td className={`p-3 ${t.side === 'BUY' ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>{t.side}</td>
                        <td className="p-3">{t.proposed_quantity?.toFixed(2)} / {t.filled_quantity?.toFixed(2) || '?'}</td>
                        <td className="p-3">{t.order_type}</td>
                        <td className="p-3">${t.actual_fill_price?.toFixed(2) || 'N/A'}</td>
                        <td className="p-3">{t.alpaca_order_id || 'N/A'}</td>
                        <td className="p-3">{t.order_status}</td>
                      </tr>
                    ))}
                  </tbody>
               </table>
             </div>
          </div>
        )}
"""

text = text.replace("{activeTab === 'MODEL SCORECARD'", ledger_view + "\n\n        {activeTab === 'MODEL SCORECARD'")

with open('/Users/supryo/Desktop/Kronos-master/frontend/app/paper-trading/page.tsx', 'w') as f:
    f.write(text)

