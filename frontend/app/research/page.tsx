'use client';

import React, { useState } from 'react';
import { runResearch, getLatestResearch } from '@/lib/api';

interface ResearchReport {
  symbol: string;
  company_name: string;
  generated_at: string;
  sector: string;
  business_summary: string;
  moat_analysis: string;
  moat_score: number;
  business_quality_score: number;
  financial_health: {
    revenue_usd_b: number;
    net_income_usd_b: number;
    gross_margin_pct: number;
    operating_margin_pct: number;
    roe_pct: number;
    fcf_usd_b: number;
    cash_usd_b: number;
    debt_usd_b: number;
    debt_to_equity: number;
  };
  valuation: {
    pe_ratio: number;
    pb_ratio: number;
    ps_ratio: number;
    ev_ebitda: number;
    dcf_fair_value: number;
    margin_of_safety_pct: number;
  };
  catalysts: string[];
  risks: string[];
  investment_thesis: string;
  buffett_score: number;
  overall_rating: 'BUY' | 'HOLD' | 'SELL';
}

export default function AIResearchAssistant() {
  const [symbol, setSymbol] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ResearchReport | null>(null);

  const handleGenerate = async () => {
    if (!symbol) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runResearch(symbol.toUpperCase());
      if (res.data?.success && res.data?.report) {
        setReport(res.data?.report);
      } else {
        setError('Failed to generate research report.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during generation.');
    } finally {
      setLoading(false);
    }
  };

  const formattedDate = report ? new Date(report.generated_at).toLocaleString() : '';
  const getRatingColor = (rating: string) => {
     if (rating === 'BUY') return 'text-[var(--color-signal-lime)] border-[var(--color-signal-lime)]';
     if (rating === 'HOLD') return 'text-[var(--color-chalk)] border-[var(--color-chalk)]';
     return 'text-[#ff4a4a] border-[#ff4a4a]';
  };

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-6 pt-[80px] space-y-[40px]">

        {/* Header Options */}
        <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[24px] flex flex-col sm:flex-row gap-[16px] justify-between items-end">
           <div className="flex flex-col gap-2 w-full max-w-sm">
             <label className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-smoke)]">
               TARGET SYMBOL
             </label>
             <input
               type="text"
               value={symbol}
               onChange={(e) => setSymbol(e.target.value)}
               className="bg-transparent border border-[var(--color-slate)] p-2 text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none uppercase"
             />
           </div>
           <button
             onClick={handleGenerate}
             disabled={loading || !symbol}
             className="px-[32px] h-[44px] bg-[var(--color-signal-lime)] text-[var(--color-void-black)] text-ui-sans text-[13px] font-medium tracking-[0.08em] uppercase transition-transform active:scale-95 glow-signal disabled:opacity-50"
           >
             {loading ? 'GENERATING...' : 'GENERATE RESEARCH'}
           </button>
        </div>

        {error && (
           <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[#ff4a4a] uppercase border border-[#ff4a4a] px-4 py-2">
             {error}
           </div>
        )}

        {report && !loading && (
           <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
             <div className="flex items-center justify-between mb-8">
               <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
                 [ MARKET INTELLIGENCE · 01 ]
               </div>
               <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)]">
                 {formattedDate}
               </div>
             </div>

             <h2 className="text-display-serif font-light text-[49px] leading-[1.05] tracking-[-1px] text-[var(--color-chalk)] max-w-3xl mb-12">
               Why is <span className="italic text-[var(--color-signal-lime)]">{report.symbol}</span> moving?
             </h2>

             <div className="grid grid-cols-1 lg:grid-cols-3 gap-[40px]">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-[40px]">

                   <div>
                      <h3 className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4 border-b border-[var(--color-graphite)] pb-2">KRONOS INTERPRETATION</h3>
                      <p className="text-ui-sans text-[14px] leading-relaxed text-[var(--color-chalk)]">{report.investment_thesis}</p>
                   </div>

                   <div>
                      <h3 className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4 border-b border-[var(--color-graphite)] pb-2">MARKET CONTEXT</h3>
                      <p className="text-ui-sans text-[14px] leading-relaxed text-[var(--color-bone)] mb-4">{report.business_summary}</p>
                      <p className="text-ui-sans text-[14px] leading-relaxed text-[var(--color-bone)]">{report.moat_analysis}</p>
                   </div>

                   <div>
                      <h3 className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4 border-b border-[var(--color-graphite)] pb-2">PRICE DRIVERS</h3>
                      <ul className="space-y-4">
                         {report.catalysts.map((cat, i) => (
                           <li key={i} className="flex gap-4">
                              <span className="text-[var(--color-signal-lime)] mt-1">+</span>
                              <span className="text-ui-sans text-[14px] text-[var(--color-bone)]">{cat}</span>
                           </li>
                         ))}
                      </ul>
                   </div>

                   <div>
                      <h3 className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-4 border-b border-[var(--color-graphite)] pb-2">RISK FACTORS</h3>
                      <ul className="space-y-4">
                         {report.risks.map((risk, i) => (
                           <li key={i} className="flex gap-4">
                              <span className="text-[#ff4a4a] mt-1">-</span>
                              <span className="text-ui-sans text-[14px] text-[var(--color-bone)]">{risk}</span>
                           </li>
                         ))}
                      </ul>
                   </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-[40px]">
                   <div className="bg-[var(--surface-raised)] border border-[var(--color-graphite)] p-[24px]">
                      <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2">RATING</div>
                      <div className={`text-ui-sans text-[11px] uppercase tracking-[0.18em] border px-3 py-1 inline-block ${getRatingColor(report.overall_rating)}`}>
                         {report.overall_rating}
                      </div>

                      <div className="mt-6 space-y-4 border-t border-[var(--color-slate)] pt-4">
                         <div className="flex justify-between items-center">
                            <span className="text-ui-sans text-[11px] text-[var(--color-smoke)]">BUFFETT SCORE</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.buffett_score}</span>
                         </div>
                         <div className="flex justify-between items-center">
                            <span className="text-ui-sans text-[11px] text-[var(--color-smoke)]">MOAT SCORE</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.moat_score}</span>
                         </div>
                         <div className="flex justify-between items-center">
                            <span className="text-ui-sans text-[11px] text-[var(--color-smoke)]">BIZ QUALITY</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.business_quality_score}</span>
                         </div>
                      </div>
                   </div>

                   <div className="bg-[var(--surface-raised)] border border-[var(--color-graphite)] p-[24px]">
                      <div className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] mb-2">SECTOR CONTEXT</div>
                      <div className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.sector}</div>

                      <div className="mt-6 space-y-4 border-t border-[var(--color-slate)] pt-4">
                         <div className="flex justify-between items-center">
                            <span className="text-ui-sans text-[11px] text-[var(--color-smoke)]">P/E RATIO</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.valuation.pe_ratio.toFixed(2)}</span>
                         </div>
                         <div className="flex justify-between items-center">
                            <span className="text-ui-sans text-[11px] text-[var(--color-smoke)]">P/B RATIO</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.valuation.pb_ratio.toFixed(2)}</span>
                         </div>
                         <div className="flex justify-between items-center">
                            <span className="text-ui-sans text-[11px] text-[var(--color-smoke)]">P/S RATIO</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-chalk)]">{report.valuation.ps_ratio.toFixed(2)}</span>
                         </div>
                         <div className="flex justify-between items-center font-bold">
                            <span className="text-ui-sans text-[11px] text-[var(--color-signal-lime)]">SAFE EST.</span>
                            <span className="text-code-mono text-[14px] text-[var(--color-signal-lime)]">${report.valuation.dcf_fair_value.toFixed(2)}</span>
                         </div>
                      </div>
                   </div>
                </div>
             </div>
           </section>
        )}

      </div>
    </div>
  );
}