'use client';

import React from 'react';

export default function RiskEnginePage() {
  // Mock data to demonstrate the UI (normally fetched from an API)
  const riskData = {
    global_exposure: 42.5,
    max_drawdown: -4.2,
    concentration: {
      "AAPL": 15.2,
      "MSFT": 12.0,
      "NVDA": 8.5
    },
    stop_levels: [
      { symbol: "AAPL", current: 220.00, stop: 210.50, distance: 4.3 },
      { symbol: "MSFT", current: 415.00, stop: 395.00, distance: 4.8 }
    ],
    risk_reward_ratio: 2.4
  };

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[40px]">

        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ RISK ENGINE ]
          </div>

          <h2 className="text-display-serif font-light text-[49px] leading-[1.05] tracking-[-1px] text-[var(--color-chalk)] mb-[80px]">
             Risk & <span className="italic text-[var(--color-signal-lime)]">Exposure.</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[40px] mb-[80px]">
             <div>
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2 border-b border-[var(--color-graphite)] pb-2">EXPOSURE</div>
                <div className="text-code-mono text-[32px] text-[var(--color-chalk)]">{riskData.global_exposure}%</div>
             </div>
             <div>
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2 border-b border-[var(--color-graphite)] pb-2">MAX LOSS (EST)</div>
                <div className="text-code-mono text-[32px] text-[#ff4a4a]">{riskData.max_drawdown}%</div>
             </div>
             <div>
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2 border-b border-[var(--color-graphite)] pb-2">POSITION SIZE CAP</div>
                <div className="text-code-mono text-[32px] text-[var(--color-chalk)]">15%</div>
             </div>
             <div>
                <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2 border-b border-[var(--color-graphite)] pb-2">RISK / REWARD</div>
                <div className="text-code-mono text-[32px] text-[var(--color-signal-lime)]">{riskData.risk_reward_ratio}</div>
             </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-[80px]">
             {/* Concentration */}
             <div>
                <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-6">
                  [ POSITION CONCENTRATION ]
                </div>
                <div className="space-y-4">
                   {Object.entries(riskData.concentration).map(([sym, pct]) => (
                      <div key={sym} className="flex items-center gap-4">
                         <div className="w-16 text-ui-sans text-[13px] text-[var(--color-chalk)] font-medium">{sym}</div>
                         <div className="flex-1 bg-[var(--surface-raised)] border border-[var(--color-graphite)] h-[6px]">
                            <div className="h-full bg-[var(--color-smoke)]" style={{ width: `${(pct / 15) * 100}%` }}></div>
                         </div>
                         <div className="w-12 text-right text-code-mono text-[13px] text-[var(--color-ash)]">{pct}%</div>
                      </div>
                   ))}
                </div>
             </div>

             {/* Stop Levels */}
             <div>
                <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-6">
                  [ STOP LEVELS ]
                </div>
                <div className="border border-[var(--color-graphite)]">
                   <div className="flex bg-[var(--surface-raised)] border-b border-[var(--color-graphite)] p-4 text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">
                      <div className="flex-1">SYMBOL</div>
                      <div className="w-24 text-right">CURRENT</div>
                      <div className="w-24 text-right">STOP</div>
                      <div className="w-24 text-right">DIST</div>
                   </div>
                   {riskData.stop_levels.map((stop) => (
                      <div key={stop.symbol} className="flex p-4 border-b border-[var(--color-graphite)] last:border-0 bg-[var(--surface-card)]">
                         <div className="flex-1 text-ui-sans text-[13px] text-[var(--color-chalk)] font-medium">{stop.symbol}</div>
                         <div className="w-24 text-right text-code-mono text-[13px] text-[var(--color-chalk)]">${stop.current.toFixed(2)}</div>
                         <div className="w-24 text-right text-code-mono text-[13px] text-[#ff4a4a] border border-[#ff4a4a] px-1">${stop.stop.toFixed(2)}</div>
                         <div className="w-24 text-right text-code-mono text-[13px] text-[var(--color-ash)]">{stop.distance.toFixed(1)}%</div>
                      </div>
                   ))}
                </div>
             </div>
          </div>
        </section>
      </div>
    </div>
  );
}