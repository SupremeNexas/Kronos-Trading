import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[var(--surface-canvas)] font-ui-sans overflow-hidden">
      <main className="flex-1 w-full max-w-[var(--layout-page-max-width)] mx-auto relative pt-[80px] pb-[120px] px-6">

        {/* Dotted Globe (pointillism dots) */}
        <div className="absolute top-[10%] right-[-10%] w-[800px] h-[800px] opacity-40 pointer-events-none -z-10">
          <svg viewBox="0 0 400 400" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="dots" width="8" height="8" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1.2" fill="#ffffff" />
              </pattern>
              <radialGradient id="fade" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <stop offset="0%" stopColor="#000" stopOpacity="1" />
                <stop offset="70%" stopColor="#000" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#000" stopOpacity="0" />
              </radialGradient>
            </defs>
            <mask id="mapMask">
              <image href="https://raw.githubusercontent.com/d3/d3-geo/master/img/graticule.png" style={{ display: 'none' }} />
              <circle cx="200" cy="200" r="180" fill="url(#fade)" />
            </mask>
            {/* Purely decorative dots mask */}
            <rect width="100%" height="100%" fill="url(#dots)" mask="url(#mapMask)" />
          </svg>
        </div>

        {/* Hero Section */}
        <section className="flex flex-col items-center text-center mt-[10vh] max-w-4xl mx-auto z-10 relative">

          {/* Metadata Eyebrow */}
          <div className="text-[11px] font-medium tracking-[0.22em] text-[var(--color-ash)] uppercase mb-8">
            [ AI-POWERED MARKET INTELLIGENCE ]
          </div>

          {/* Display Headline */}
          <h1 className="text-display-serif font-light text-[56px] md:text-[89px] leading-[0.94] tracking-[-3.1px] text-[var(--color-chalk)] mb-8">
            Markets change.<br />
            Kronos finds the <span className="italic text-[var(--color-signal-lime)]">signal.</span>
          </h1>

          {/* Subtext */}
          <div className="text-[14px] leading-relaxed text-[var(--color-bone)] max-w-[480px] mx-auto mb-12">
            Real market data. AI-driven analysis. Paper execution.
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-[24px] items-center justify-center">
            <Link
              href="/dashboard"
              className="inline-flex h-[44px] items-center justify-center rounded-[4px] bg-[var(--color-signal-lime)] px-[32px] text-[14px] font-medium text-[var(--color-void-black)] transition-transform active:scale-95 glow-signal"
            >
              OPEN KRONOS
            </Link>
            <Link
              href="/analysis"
              className="inline-flex h-[44px] items-center justify-center rounded-[4px] border border-[var(--color-signal-lime)] px-[32px] text-[14px] font-medium text-[var(--color-signal-lime)] bg-transparent uppercase tracking-[0.08em] transition-transform active:scale-95 glow-signal"
            >
              EXPLORE ANALYSIS
            </Link>
          </div>
        </section>

      </main>

      {/* Neon Section Divider */}
      <div className="w-full h-[6px] bg-[var(--color-signal-lime)]"></div>

      <footer className="bg-[var(--color-carbon)] py-[48px] px-6 text-center border-t border-[var(--color-graphite)]">
        <p className="text-[12px] text-[var(--color-ash)] max-w-4xl mx-auto">
          <span className="font-semibold text-[var(--color-smoke)] block mb-2 uppercase tracking-[0.1em] text-[11px]">Informational Use Only</span>
          Kronos AI Market Intelligence is a quantitative analytical tool. Model forecasts, backtests, and AI commentary do not constitute financial or investment advice. Probabilities and target prices are mathematical estimates, not guaranteed outcomes.
        </p>
      </footer>
    </div>
  );
}
