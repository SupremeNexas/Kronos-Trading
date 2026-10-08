
with open('frontend/app/trades/page.tsx', 'r') as f:
    text = f.read()

thead_old = '''             <thead>
               <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                 <th className="py-2">Date</th>
                 <th className="py-2">Symbol</th>
                 <th className="py-2">Side</th>
                 <th className="py-2">Qty</th>
                 <th className="py-2">Filled Qty</th>
                 <th className="py-2">Order Type</th>
                 <th className="py-2">Limit Price</th>
                 <th className="py-2">Fill Price</th>
                 <th className="py-2">Status</th>
                 <th className="py-2">Alpaca ID</th>
               </tr>
             </thead>
             <tbody>
               {trades.length === 0 && (
                 <tr>
                   <td colSpan={10} className="py-4 text-center text-[var(--color-smoke)]">No trades found.</td>
                 </tr>
               )}
               {trades.map((t, i) => (
                 <tr key={i} className="border-b border-[var(--color-graphite)]/50 hover:bg-[var(--surface-hover)]">
                   <td className="py-2">{t.date}</td>
                   <td className="py-2">{t.symbol}</td>
                   <td className={`py-2 ${t.side==='BUY'?'text-[var(--color-signal-lime)]':'text-[#ff4a4a]'}`}>{t.side}</td>
                   <td className="py-2">{t.quantity}</td>
                   <td className="py-2">{t.filled_quantity}</td>
                   <td className="py-2">{t.order_type}</td>
                   <td className="py-2">{t.limit_price || '-'}</td>
                   <td className="py-2">{t.fill_price || '-'}</td>
                   <td className="py-2">{t.status}</td>
                   <td className="py-2 text-[10px] text-[var(--color-smoke)]" title={t.order_id}>{t.order_id?.substring(0,8)}...</td>
                 </tr>
               ))}
             </tbody>'''

thead_new = '''             <thead>
               <tr className="border-b border-[var(--color-graphite)] text-[var(--color-smoke)]">
                 <th className="py-2">Date</th>
                 <th className="py-2">Symbol</th>
                 <th className="py-2">Tactic</th>
                 <th className="py-2">Side</th>
                 <th className="py-2 text-right">Qty/Fill</th>
                 <th className="py-2 text-right">Limit/Fill Price</th>
                 <th className="py-2 text-right">Realized P&L</th>
                 <th className="py-2">Status</th>
                 <th className="py-2">Reasoning</th>
                 <th className="py-2">Alpaca ID</th>
               </tr>
             </thead>
             <tbody>
               {trades.length === 0 && (
                 <tr>
                   <td colSpan={10} className="py-4 text-center text-[var(--color-smoke)]">No trades found.</td>
                 </tr>
               )}
               {trades.map((t, i) => (
                 <tr key={i} className="border-b border-[var(--color-graphite)]/50 hover:bg-[var(--surface-hover)]">
                   <td className="py-3 text-xs">{t.date}</td>
                   <td className="py-3 font-bold">{t.symbol}</td>
                   <td className="py-3"><span className="px-2 py-1 bg-[#222] border border-[#333] text-[10px]">{t.tactic}</span></td>
                   <td className={`py-3 ${t.side==='BUY'?'text-[var(--color-signal-lime)]':'text-[#ff4a4a]'}`}>{t.side}</td>
                   <td className="py-3 text-right">{t.quantity} / {t.filled_quantity}</td>
                   <td className="py-3 text-right">
                     {t.limit_price ? `$${t.limit_price}` : 'MKT'} <br/>
                     <span className="text-[#888]">{t.fill_price ? `$${t.fill_price}` : '-'}</span>
                   </td>
                   <td className={`py-3 text-right font-bold ${t.realized_pnl !== null && t.realized_pnl > 0 ? 'text-[var(--color-signal-lime)]' : (t.realized_pnl !== null && t.realized_pnl < 0 ? 'text-[#ff4a4a]' : '')}`}>
                     {t.realized_pnl !== null ? (t.realized_pnl > 0 ? `+$${t.realized_pnl.toFixed(2)}` : `-$${Math.abs(t.realized_pnl).toFixed(2)}`) : '-'}
                   </td>
                   <td className="py-3 text-xs">{t.status}</td>
                   <td className="py-3 text-[11px] text-[var(--color-smoke)] max-w-[200px] truncate" title={t.reasoning || t.notes}>{t.reasoning || t.notes || '-'}</td>
                   <td className="py-3 text-[10px] text-[var(--color-smoke)]" title={t.order_id}>{t.order_id?.substring(0,8)}...</td>
                 </tr>
               ))}
             </tbody>'''

text = text.replace(thead_old, thead_new)

with open('frontend/app/trades/page.tsx', 'w') as f:
    f.write(text)
print("Updated Trades UI")
