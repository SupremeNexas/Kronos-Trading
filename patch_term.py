
import re
import os

with open('frontend/app/terminal/page.tsx', 'r') as f:
    text = f.read()

# 1. Add states
state_insertion = '''
  const [tactics, setTactics] = useState<any[]>([]);
  const [selectedTactic, setSelectedTactic] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [notes, setNotes] = useState('');
'''
text = text.replace("const [limitPrice, setLimitPrice] = useState(0);", "const [limitPrice, setLimitPrice] = useState(0);\n" + state_insertion)


# 2. Add useEffect for tactics
eff_insertion = '''
  useEffect(() => {
    fetchAccountData();
    axios.get('/api/tactics').then(res => {
        if(res.data.success) {
            setTactics(res.data.tactics);
            if (res.data.tactics.length > 0) setSelectedTactic(res.data.tactics[0].id);
        }
    }).catch(console.error);
    const interval = setInterval(fetchAccountData, 5000);
    return () => clearInterval(interval);
  }, []);
'''
text = re.sub(r'useEffect\(\(\) => \{\n    fetchAccountData\(\);\n    const interval = setInterval\(fetchAccountData, 5000\);\n    return \(\) => clearInterval\(interval\);\n  \}, \[\]\);', eff_insertion, text)

# 3. Add to payload
payload_old = '''      const payload = {
        symbol,
        side,
        quantity,
        order_type: orderType,
        price: orderType === 'Limit' ? limitPrice : 0,
        analysis_id: forecast?.analysis_id,
        strategy: strategyParam || undefined,
        signal_scan_id: scanIdParam || undefined,
        signal_score: scoreParam || undefined,
        volume_ratio: volParam || undefined,
        attention_score: attentionParam || undefined,
        momentum_7d: momentumParam || undefined,
        decision: strategyParam ? "MANUAL_TRADE" : undefined
      };'''

payload_new = '''      let tName = tactics.find(t=>t.id === selectedTactic)?.name || '';
      const payload = {
        symbol,
        side,
        quantity,
        order_type: orderType,
        price: orderType === 'Limit' ? limitPrice : 0,
        tactic_id: selectedTactic,
        tactic_name: tName,
        reasoning,
        notes,
        analysis_id: forecast?.analysis_id,
        strategy: strategyParam || undefined,
        signal_scan_id: scanIdParam || undefined,
        signal_score: scoreParam || undefined,
        volume_ratio: volParam || undefined,
        attention_score: attentionParam || undefined,
        momentum_7d: momentumParam || undefined,
        decision: strategyParam ? "MANUAL_TRADE" : undefined
      };'''
text = text.replace(payload_old, payload_new)

# 4. Add UI fields before CONFIRM ORDER button
ui_old = '''                </div>

                <button onClick={handlePlaceOrder} className={`w-full py-3 mt-6 font-bold tracking-[0.1em] text-black ${side==='BUY' ? 'bg-[var(--color-signal-lime)] hover:bg-[#86ff55]' : 'bg-[#ff4a4a] hover:bg-[#ff6b6b]'}`}>
                  CONFIRM {side} ORDER
                </button>
              </div>'''

ui_new = '''                </div>

                <div className="mt-4 pt-4 border-t border-[var(--color-graphite)]">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] text-[var(--color-smoke)] tracking-wider">TACTIC (REQUIRED)</span>
                  </div>
                  <select value={selectedTactic} onChange={e => setSelectedTactic(e.target.value)} className="w-full bg-[#111] border border-[var(--color-graphite)] text-white p-2">
                    {tactics.map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>

                <div className="mt-4">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] text-[var(--color-smoke)] tracking-wider">REASONING / THESIS</span>
                  </div>
                  <textarea value={reasoning} onChange={e => setReasoning(e.target.value)} rows={2} className="w-full bg-[#111] border border-[var(--color-graphite)] text-[#ccc] p-2 text-sm" placeholder="Why are you making this trade?"></textarea>
                </div>

                <div className="mt-4">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] text-[var(--color-smoke)] tracking-wider">JOURNAL NOTES & RISK</span>
                  </div>
                  <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full bg-[#111] border border-[var(--color-graphite)] text-[#ccc] p-2 text-sm" placeholder="Additional observations, risk limits..."></textarea>
                </div>

                <button
                  onClick={handlePlaceOrder}
                  disabled={!selectedTactic}
                  className={`w-full py-3 mt-6 font-bold tracking-[0.1em] text-black disabled:opacity-50 ${side==='BUY' ? 'bg-[var(--color-signal-lime)] hover:bg-[#86ff55]' : 'bg-[#ff4a4a] hover:bg-[#ff6b6b]'}`}>
                  CONFIRM {side} ORDER {account?.trading_mode === 'PAPER' ? '(PAPER)' : ''}
                </button>
              </div>'''

text = text.replace(ui_old, ui_new)


with open('frontend/app/terminal/page.tsx', 'w') as f:
    f.write(text)

