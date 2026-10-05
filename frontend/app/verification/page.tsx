"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import { cn } from "@/lib/utils";

type StatusType = "VERIFIED" | "PARTIAL" | "FAILED" | "NOT VERIFIED" | "OPERATIONAL" | "DEGRADED";

export default function VerificationPage() {
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [currentRun, setCurrentRun] = useState<any>(null);
  const [tab, setTab] = useState<"CURRENT" | "HISTORY">("CURRENT");

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("/api/verification/history");
      setHistory(res.data);
      if (res.data && res.data.length > 0) {
        setCurrentRun(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const runVerification = async () => {
    setLoading(true);
    try {
      const res = await axios.post("/api/verification/run");
      setCurrentRun(res.data);
      await fetchHistory();
      setTab("CURRENT");
    } catch (err) {
      console.error("Verification failed", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: StatusType) => {
    switch (status) {
      case "VERIFIED":
      case "OPERATIONAL":
        return "text-[var(--color-emerald)] border-[var(--color-emerald)]";
      case "PARTIAL":
        return "text-[var(--color-gold)] border-[var(--color-gold)]";
      case "FAILED":
      case "DEGRADED":
        return "text-[var(--color-crimson)] border-[var(--color-crimson)]";
      default:
        return "text-[var(--color-slate)] border-[var(--color-slate)]";
    }
  };

  return (
    <div className="w-full flex justify-center pb-20">
      <div className="w-full max-w-[var(--layout-page-max-width)] px-4 md:px-8 mt-8 flex flex-col gap-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
          <div>
            <h1 className="text-display-serif text-3xl md:text-4xl">KRONOS SYSTEM PROOF</h1>
            <p className="text-[var(--color-slate)] font-mono text-sm mt-2 uppercase tracking-wide">
              Live implementation, deployment and capability verification
            </p>
          </div>
          <button 
            onClick={runVerification} 
            disabled={loading}
            className="flex items-center gap-2 border border-[var(--color-graphite)] hover:border-[var(--color-emerald)] bg-[var(--color-ink)] px-6 py-3 font-mono text-sm tracking-wide uppercase transition-colors"
          >
            {loading ? (
              <>
                <span className="w-2 h-2 rounded-full bg-[var(--color-emerald)] animate-pulse" />
                VERIFYING...
              </>
            ) : (
              <>RUN FULL SYSTEM VERIFICATION</>
            )}
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 border-b border-[var(--color-graphite)] font-mono text-xs mt-4">
          <button
            onClick={() => setTab("CURRENT")}
            className={cn(
              "px-6 py-3 uppercase tracking-wider transition-colors",
              tab === "CURRENT" ? "border-t border-l border-r border-[var(--color-graphite)] bg-[var(--color-void-black)] text-white relative top-[1px]" : "text-[var(--color-slate)]"
            )}
          >
            CURRENT RUN
          </button>
          <button
            onClick={() => setTab("HISTORY")}
            className={cn(
              "px-6 py-3 uppercase tracking-wider transition-colors",
              tab === "HISTORY" ? "border-t border-l border-r border-[var(--color-graphite)] bg-[var(--color-void-black)] text-white relative top-[1px]" : "text-[var(--color-slate)]"
            )}
          >
            HISTORY ({history.length})
          </button>
        </div>

        {tab === "CURRENT" && currentRun && (
          <div className="flex flex-col gap-6 animate-in">
            {/* Overview Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="border border-[var(--color-graphite)] bg-[var(--color-ink)] p-5 flex flex-col justify-between">
                <span className="font-mono text-[10px] text-[var(--color-slate)] uppercase">SYSTEM STATUS</span>
                <span className={cn("font-mono text-xl mt-2 font-bold", getStatusColor(currentRun.overall_status))}>
                  {currentRun.overall_status}
                </span>
              </div>
              <div className="border border-[var(--color-graphite)] bg-[var(--color-ink)] p-5 flex flex-col justify-between">
                <span className="font-mono text-[10px] text-[var(--color-slate)] uppercase">LAST VERIFIED</span>
                <span className="font-mono text-sm mt-2">{new Date(currentRun.timestamp).toLocaleString()}</span>
              </div>
              <div className="border border-[var(--color-graphite)] bg-[var(--color-ink)] p-5 flex flex-col justify-between">
                <span className="font-mono text-[10px] text-[var(--color-slate)] uppercase">ENVIRONMENT</span>
                <span className="font-mono text-sm mt-2">{currentRun.environment?.deployment || "UNKNOWN"}</span>
              </div>
              <div className="border border-[var(--color-graphite)] bg-[var(--color-ink)] p-5 flex flex-col justify-between">
                <span className="font-mono text-[10px] text-[var(--color-slate)] uppercase">DEPLOYMENT SHA</span>
                <span className="font-mono text-sm mt-2">{currentRun.environment?.git_sha?.substring(0, 7) || "---"}</span>
              </div>
            </div>

            {/* Counts */}
            <div className="grid grid-cols-4 gap-4 border border-[var(--color-graphite)] p-3 bg-[var(--color-void-black)] mt-2">
              <div className="flex flex-col items-center">
                <span className="font-mono text-[10px] text-[var(--color-slate)]">VERIFIED</span>
                <span className="font-mono text-lg text-[var(--color-emerald)]">{currentRun.counts?.VERIFIED || 0}</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="font-mono text-[10px] text-[var(--color-slate)]">PARTIAL</span>
                <span className="font-mono text-lg text-[var(--color-gold)]">{currentRun.counts?.PARTIAL || 0}</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="font-mono text-[10px] text-[var(--color-slate)]">FAILED</span>
                <span className="font-mono text-lg text-[var(--color-crimson)]">{currentRun.counts?.FAILED || 0}</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="font-mono text-[10px] text-[var(--color-slate)]">NOT VERIFIED</span>
                <span className="font-mono text-lg text-[var(--color-slate)]">{currentRun.counts?.["NOT VERIFIED"] || 0}</span>
              </div>
            </div>

            {/* Claim vs Evidence Section */}
            {currentRun.claims_vs_evidence && currentRun.claims_vs_evidence.length > 0 && (
              <div className="mt-8">
                <h3 className="font-serif text-xl border-b border-[var(--color-graphite)] pb-2 mb-4">CLAIMED VS VERIFIED</h3>
                <div className="flex flex-col gap-3">
                  {currentRun.claims_vs_evidence.map((c: any, i: number) => (
                    <div key={i} className="border border-[var(--color-graphite)] flex flex-col md:flex-row text-sm">
                      <div className="md:w-1/3 p-4 bg-[var(--color-void-black)] border-r border-[var(--color-graphite)]">
                        <span className="block font-mono text-[10px] text-[var(--color-slate)] mb-1 uppercase">CLAIM</span>
                        <div className="font-mono">{c.claim}</div>
                      </div>
                      <div className="md:w-1/2 p-4 bg-[var(--color-ink)]">
                        <span className="block font-mono text-[10px] text-[var(--color-slate)] mb-1 uppercase">EVIDENCE</span>
                        <div className="font-mono text-xs">{c.evidence}</div>
                      </div>
                      <div className="md:w-1/6 p-4 flex items-center justify-center bg-[var(--color-void-black)] border-l border-[var(--color-graphite)]">
                        <span className={cn("font-mono text-xs font-bold border px-2 py-1", getStatusColor(c.status))}>
                          {c.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Feature Inventory */}
            <div className="mt-8">
              <h3 className="font-serif text-xl border-b border-[var(--color-graphite)] pb-2 mb-4">FEATURE INVENTORY</h3>
              <div className="border border-[var(--color-graphite)] bg-[var(--color-ink)] overflow-x-auto">
                <table className="w-full text-left font-mono text-xs">
                  <thead className="bg-[var(--color-void-black)] border-b border-[var(--color-graphite)]">
                    <tr>
                      <th className="p-3 font-normal text-[var(--color-slate)]">CATEGORY</th>
                      <th className="p-3 font-normal text-[var(--color-slate)]">FEATURE</th>
                      <th className="p-3 font-normal text-[var(--color-slate)]">STATUS</th>
                      <th className="p-3 font-normal text-[var(--color-slate)] border-l border-[var(--color-graphite)]">EVIDENCE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentRun.features?.map((f: any, i: number) => (
                      <tr key={i} className="border-b border-[var(--color-graphite)] last:border-0 hover:bg-[var(--color-void-black)] transition-colors">
                        <td className="p-3">{f.category}</td>
                        <td className="p-3 font-bold">{f.name}</td>
                        <td className="p-3">
                          <span className={cn(getStatusColor(f.status))}>
                            {f.status}
                          </span>
                        </td>
                        <td className="p-3 border-l border-[var(--color-graphite)] text-[var(--color-slate)]">
                          <pre className="font-mono text-[10px] max-w-md overflow-x-auto">
                            {JSON.stringify(f.evidence, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {tab === "CURRENT" && !currentRun && !loading && (
          <div className="py-20 flex flex-col items-center justify-center font-mono text-sm text-[var(--color-slate)]">
            <p>No verification run found.</p>
            <p className="mt-2 text-xs">Click "RUN FULL SYSTEM VERIFICATION" to begin.</p>
          </div>
        )}

        {tab === "HISTORY" && (
          <div className="animate-in flex flex-col gap-4">
            {history.map((run: any, i: number) => (
              <div key={i} className="border border-[var(--color-graphite)] p-4 flex justify-between items-center bg-[var(--color-ink)]">
                <div>
                  <div className="font-mono text-sm text-[var(--color-slate)]">{new Date(run.timestamp).toLocaleString()}</div>
                  <div className="font-mono text-xs mt-1">ID: {run.verification_id}</div>
                </div>
                <div>
                  <span className={cn("font-mono text-sm", getStatusColor(run.overall_status))}>
                    {run.overall_status}
                  </span>
                </div>
              </div>
            ))}
            {history.length === 0 && (
              <div className="py-10 text-center font-mono text-sm text-[var(--color-slate)] border border-[var(--color-graphite)] border-dashed">
                No past runs available.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
