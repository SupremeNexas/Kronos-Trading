'use client';

import React, { useState } from 'react';
import { runResearch, getLatestResearch } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
  FileSearch, Activity, ShieldCheck,
  TrendingUp, TrendingDown, AlertTriangle,
  CheckCircle2, DollarSign, BarChart3,
  RefreshCw, Loader2, Briefcase, Clock
} from 'lucide-react';

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

  const handleLoadLatest = async () => {
    if (!symbol) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getLatestResearch(symbol.toUpperCase());
      if (res.data?.success && res.data?.report) {
        setReport(res.data?.report);
      } else {
        setError('No recent report found or failed to load.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while loading.');
    } finally {
      setLoading(false);
    }
  };

  const formattedDate = report ? new Date(report.generated_at).toLocaleString() : '';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex items-start gap-4">
          <div className="p-3 bg-slate-900 rounded-xl border border-slate-800">
            <FileSearch className="w-8 h-8 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AI Research Assistant</h1>
            <p className="text-slate-400 mt-1">Berkshire-Style Fundamental Analysis</p>
          </div>
        </div>

        {/* Controls */}
        <div className="fintech-card p-6 bg-slate-900/50 rounded-xl border border-slate-800">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="w-full sm:w-64 space-y-2">
              <label htmlFor="symbol" className="text-sm font-medium text-slate-400 uppercase tracking-wider">
                Ticker Symbol
              </label>
              <input
                id="symbol"
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-slate-50 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors uppercase"
                placeholder="e.g. AAPL"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading || !symbol}
              className="w-full sm:w-auto px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Activity className="w-5 h-5" />}
              Generate Deep Research
            </button>

            <button
              onClick={handleLoadLatest}
              disabled={loading || !symbol}
              className="w-full sm:w-auto px-6 py-2.5 border border-slate-700 hover:bg-slate-800 text-slate-200 font-medium rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className="w-5 h-5" />
              Load Latest
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-rose-950/20 border border-rose-900/50 text-rose-400 p-4 rounded-xl flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="fintech-card p-8 rounded-xl border border-slate-800 space-y-8 animate-pulse bg-slate-900/40">
            <div className="flex items-center justify-center flex-col gap-4 py-12">
              <Loader2 className="w-12 h-12 text-cyan-500 animate-spin" />
              <p className="text-lg text-slate-300 font-medium text-center">
                Analyzing fundamentals, financial statements, and competitive moat...
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="h-32 bg-slate-800/50 rounded-xl"></div>
              <div className="h-32 bg-slate-800/50 rounded-xl"></div>
              <div className="h-32 bg-slate-800/50 rounded-xl"></div>
            </div>
            <div className="h-48 bg-slate-800/50 rounded-xl"></div>
          </div>
        )}

        {/* Report Content */}
        {!loading && report && !error && (
          <div className="space-y-6 animate-in fade-in duration-500">

            {/* Report Header */}
            <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-3xl font-bold text-slate-50">{report.company_name}</h2>
                  <span className="px-3 py-1 bg-slate-800 text-cyan-400 rounded-lg text-sm font-semibold tracking-wider border border-cyan-900/30">
                    {report.symbol}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-400">
                  <span className="flex items-center gap-1"><Briefcase className="w-4 h-4" /> {report.sector}</span>
                  <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> {formattedDate}</span>
                </div>
              </div>

              <div className={cn(
                "px-6 py-3 rounded-xl flex text-lg font-bold items-center gap-2 border",
                report.overall_rating === 'BUY' ? "bg-emerald-950/40 text-emerald-400 border-emerald-900/50" :
                report.overall_rating === 'HOLD' ? "bg-amber-950/40 text-amber-400 border-amber-900/50" :
                "bg-rose-950/40 text-rose-400 border-rose-900/50"
              )}>
                {report.overall_rating === 'BUY' && <TrendingUp className="w-6 h-6" />}
                {report.overall_rating === 'HOLD' && <Activity className="w-6 h-6" />}
                {report.overall_rating === 'SELL' && <TrendingDown className="w-6 h-6" />}
                RATING: {report.overall_rating}
              </div>
            </div>

            {/* Score Cards Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ScoreCard title="Buffett Score" score={report.buffett_score} icon={<ShieldCheck className="w-6 h-6 text-emerald-400" />} />
              <ScoreCard title="Moat Score" score={report.moat_score} icon={<ShieldCheck className="w-6 h-6 text-cyan-400" />} />
              <ScoreCard title="Business Quality" score={report.business_quality_score} icon={<ShieldCheck className="w-6 h-6 text-indigo-400" />} />
            </div>

            {/* Two Column Layout for Main Data */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* Left Column (Wider) */}
              <div className="lg:col-span-2 space-y-6">

                {/* Investment Thesis (Highlight) */}
                <div className="fintech-card p-8 bg-slate-900/80 border-l-4 border-l-cyan-500 rounded-xl rounded-l-none border-y border-y-slate-800 border-r border-r-slate-800">
                  <h3 className="text-sm font-semibold text-cyan-500 uppercase tracking-wider mb-4">Investment Thesis</h3>
                  <blockquote className="text-xl leading-relaxed text-slate-200 font-serif italic text-balance">
                    "{report.investment_thesis}"
                  </blockquote>
                </div>

                {/* Business & Moat */}
                <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-slate-400" />
                    Business & Moat Analysis
                  </h3>
                  <div className="space-y-4 text-slate-300 leading-relaxed">
                    <div>
                      <h4 className="text-sm font-medium text-slate-400 mb-1">Business Summary</h4>
                      <p>{report.business_summary}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-400 mb-1">Moat Analysis</h4>
                      <p>{report.moat_analysis}</p>
                    </div>
                  </div>
                </div>

                {/* Financial Health Grid */}
                <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-slate-400" />
                    Financial Health
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <DataPoint label="Revenue (Billions)" value={`$${report.financial_health.revenue_usd_b}B`} />
                    <DataPoint label="Net Income" value={`$${report.financial_health.net_income_usd_b}B`} />
                    <DataPoint label="Gross Margin" value={`${report.financial_health.gross_margin_pct}%`} />
                    <DataPoint label="Operating Margin" value={`${report.financial_health.operating_margin_pct}%`} />
                    <DataPoint label="ROE" value={`${report.financial_health.roe_pct}%`} />
                    <DataPoint label="Free Cash Flow" value={`$${report.financial_health.fcf_usd_b}B`} />
                    <DataPoint label="Cash Position" value={`$${report.financial_health.cash_usd_b}B`} />
                    <DataPoint label="Total Debt" value={`$${report.financial_health.debt_usd_b}B`} />
                  </div>
                </div>

              </div>

              {/* Right Column (Sidebar) */}
              <div className="space-y-6">

                {/* Valuation */}
                <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-slate-400" />
                    Valuation Profile
                  </h3>

                  {/* Margin of Safety Focus */}
                  <div className="mb-6 p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="text-sm text-slate-400 mb-1">DCF Fair Value Estimate</div>
                    <div className="text-3xl font-bold text-slate-50">${report.valuation.dcf_fair_value.toFixed(2)}</div>

                    <div className={cn(
                      "mt-2 text-sm font-medium flex items-center gap-1",
                      report.valuation.margin_of_safety_pct > 0 ? "text-emerald-400" : "text-rose-400"
                    )}>
                      {report.valuation.margin_of_safety_pct > 0 ? "+" : ""}
                      {report.valuation.margin_of_safety_pct}% Margin of Safety
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">P/E Ratio</span>
                      <span className="font-medium text-slate-200">{report.valuation.pe_ratio.toFixed(1)}x</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">P/B Ratio</span>
                      <span className="font-medium text-slate-200">{report.valuation.pb_ratio.toFixed(1)}x</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">P/S Ratio</span>
                      <span className="font-medium text-slate-200">{report.valuation.ps_ratio.toFixed(1)}x</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">EV/EBITDA</span>
                      <span className="font-medium text-slate-200">{report.valuation.ev_ebitda.toFixed(1)}x</span>
                    </div>
                  </div>
                </div>

                {/* Catalysts */}
                <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl">
                  <h3 className="text-lg font-semibold mb-4 text-emerald-400 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Key Catalysts
                  </h3>
                  <ul className="space-y-3">
                    {report.catalysts.map((cat, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <span>{cat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Risks */}
                <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl">
                  <h3 className="text-lg font-semibold mb-4 text-rose-400 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    Key Risks
                  </h3>
                  <ul className="space-y-3">
                    {report.risks.map((risk, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <div className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0" />
                        <span>{risk}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

function ScoreCard({ title, score, icon }: { title: string, score: number, icon: React.ReactNode }) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-emerald-400";
    if (s >= 60) return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <div className="fintech-card p-6 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between group hover:border-slate-700 transition-colors">
      <div className="space-y-1">
        <div className="text-sm font-medium text-slate-400">{title}</div>
        <div className={cn("text-4xl font-bold font-mono tracking-tight", getScoreColor(score))}>
          {score}
        </div>
      </div>
      <div className="p-4 rounded-full bg-slate-950 border border-slate-800 group-hover:scale-110 transition-transform">
        {icon}
      </div>
    </div>
  );
}

function DataPoint({ label, value }: { label: string, value: string | number }) {
  return (
    <div className="p-3 bg-slate-950/50 rounded-lg border border-slate-800/50">
      <div className="text-xs text-slate-400 mb-1 whitespace-nowrap overflow-hidden text-ellipsis">{label}</div>
      <div className="text-lg font-semibold text-slate-200">{value}</div>
    </div>
  );
}
