import Link from "next/link";
import { ArrowRight, BarChart3, Brain, Target } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative px-6 py-24 md:py-32 overflow-hidden flex flex-col items-center text-center">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950 -z-10" />

          <div className="inline-flex items-center rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-sm text-cyan-300 font-medium mb-8">
            <span className="flex h-2 w-2 rounded-full bg-cyan-500 mr-2 animate-pulse"></span>
            Kronos Foundation Model Available
          </div>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 max-w-4xl mx-auto">
            AI-Powered <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              Market Intelligence
            </span>
          </h1>

          <p className="mt-6 text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Harness the power of mathematical ensemble models and autoregressive transformers to forecast multi-horizon financial sequences with institutional-grade precision.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row gap-4 items-center justify-center">
            <Link
              href="/dashboard"
              className="inline-flex h-12 items-center justify-center rounded-md bg-cyan-600 px-8 text-sm font-medium text-white shadow transition-colors hover:bg-cyan-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-cyan-500"
            >
              Enter Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link
              href="/forecast"
              className="inline-flex h-12 items-center justify-center rounded-md border border-slate-700 bg-slate-900/50 px-8 text-sm font-medium text-slate-300 shadow-sm transition-colors hover:bg-slate-800 hover:text-slate-50"
            >
              Explore AI Models
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section className="px-6 py-24 bg-slate-950">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="glass-card p-8 rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col items-center text-center">
                <div className="h-14 w-14 rounded-full bg-cyan-500/10 flex items-center justify-center mb-6">
                  <Brain className="h-7 w-7 text-cyan-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">AI Forecasting Edge</h3>
                <p className="text-slate-400">
                  Multimodal ensemble architecture integrating TimesFM, Chronos-2, and Kronos Foundation Model for enhanced directional accuracy.
                </p>
              </div>

              <div className="glass-card p-8 rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col items-center text-center">
                <div className="h-14 w-14 rounded-full bg-blue-500/10 flex items-center justify-center mb-6">
                  <Target className="h-7 w-7 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Scientific Validation</h3>
                <p className="text-slate-400">
                  Walk-forward historical backtesting engine delivering transparent MAE, RMSE, and hit rate calibrations.
                </p>
              </div>

              <div className="glass-card p-8 rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col items-center text-center">
                <div className="h-14 w-14 rounded-full bg-emerald-500/10 flex items-center justify-center mb-6">
                  <BarChart3 className="h-7 w-7 text-emerald-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Risk-Aware Execution</h3>
                <p className="text-slate-400">
                  Built-in FinRL position sizing, trailing stop-losses, and paper portfolio engine for sophisticated strategy building.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 bg-slate-950 py-8 px-6 text-center">
        <p className="text-sm text-slate-500 max-w-4xl mx-auto">
          <span className="font-semibold text-slate-400 block mb-2">Informational Use Only</span>
          Kronos AI Market Intelligence is a quantitative analytical tool. Model forecasts, backtests, and AI commentary do not constitute financial or investment advice. Probabilities and target prices are mathematical estimates, not guaranteed outcomes. Always consult a licensed registered advisor before investing real capital.
        </p>
      </footer>
    </div>
  );
}
