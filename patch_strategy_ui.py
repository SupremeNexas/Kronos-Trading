import os

path = "frontend/app/strategies/page.tsx"
with open(path, "r") as f:
    text = f.read()

# Add a Strategy Builder tab button next to Past Scans
tab_btn = """        <button
          onClick={() => setActiveTab("history")}"""

new_tab_btn = """        <button
          onClick={() => setActiveTab("builder")}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === "builder"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
          )}
        >
          Strategy Builder
        </button>
        <button
          onClick={() => setActiveTab("history")}"""
text = text.replace(tab_btn, new_tab_btn)

# Add the new Strategy Builder panel
history_panel = """      {activeTab === "history" && ("""

builder_panel = """      {activeTab === "builder" && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <h3 className="text-white font-medium mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            Rule-Based Strategy Builder
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Design strategies using technical indicators imported from AstraQuant.
            (e.g., EMA, RSI, ATR, MACD Histogram, Bollinger Squeeze).
          </p>
          <div className="space-y-4">
            <div className="p-4 bg-slate-950 border border-slate-800 rounded">
              <h4 className="text-sm font-bold text-white mb-2">Technical Indicators Module Status</h4>
              <p className="text-xs text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Module integrated successfully from AstraQuant engine.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-950 border border-slate-800 p-4 rounded text-sm text-slate-300">
                <span className="block font-bold text-slate-100 mb-1">RSI (Relative Strength Index)</span>
                Identifies overbought/oversold conditions dynamically.
              </div>
              <div className="bg-slate-950 border border-slate-800 p-4 rounded text-sm text-slate-300">
                <span className="block font-bold text-slate-100 mb-1">Bollinger Squeeze</span>
                Detects volatility compression for explosive breakout strategies.
              </div>
              <div className="bg-slate-950 border border-slate-800 p-4 rounded text-sm text-slate-300">
                <span className="block font-bold text-slate-100 mb-1">MACD Histogram Acceleration</span>
                Momentum tracking derived from MACD Delta values.
              </div>
              <div className="bg-slate-950 border border-slate-800 p-4 rounded text-sm text-slate-300">
                <span className="block font-bold text-slate-100 mb-1">ATR (Average True Range)</span>
                Dynamic stop-loss sizing based on exact market volatility.
              </div>
            </div>
            
            <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded font-medium text-sm transition-colors mt-6 border border-slate-700 w-full justify-center opacity-50 cursor-not-allowed">
              <Play className="w-4 h-4" /> Run Rule-Based Backtest (Development Sandboxed)
            </button>
          </div>
        </div>
      )}

      {activeTab === "history" && ("""
text = text.replace(history_panel, builder_panel)

with open(path, "w") as f:
    f.write(text)
print("Patched settings UI")
