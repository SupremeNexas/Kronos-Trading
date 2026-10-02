'use client';

import React, { useState } from 'react';
import { placeOrder } from '@/lib/api';
import axios from 'axios';

export default function PaperTradingPage() {
  const [symbol, setSymbol] = useState('');
  const [workflowState, setWorkflowState] = useState<'IDLE' | 'RUNNING' | 'PENDING_CONFIRMATION' | 'COMPLETED' | 'ERROR'>('IDLE');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [proposedOrder, setProposedOrder] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);

  const [orderStatus, setOrderStatus] = useState<{type: 'success' | 'error' | null, message: string}>({type: null, message: ''});

  const runAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol) return;
    setWorkflowState('RUNNING');
    setOrderStatus({ type: null, message: '' });
    
    try {
      const res = await axios.post('/api/agent_run', { symbol: symbol.toUpperCase(), timeframe: '1d', allow_trading: true });
      if (res.data.execution?.status === 'PENDING_CONFIRMATION') {
        setProposedOrder(res.data.execution.order_info);
        setAnalysisId(res.data.analysis_id);
        setMetrics(res.data.validation?.metrics || res.data.validation?.performance_metrics);
        setWorkflowState('PENDING_CONFIRMATION');
      } else {
        setWorkflowState('ERROR');
        setOrderStatus({ type: 'error', message: res.data.execution?.reason || 'Agent run did not result in a valid trade.' });
      }
    } catch (err: any) {
      setWorkflowState('ERROR');
      setOrderStatus({ type: 'error', message: err.message || 'Error running agent' });
    }
  };

  const confirmTrade = async () => {
    if (!analysisId) return;
    setWorkflowState('RUNNING');
    try {
      const res = await axios.post('/api/trading/confirm_trade', { analysis_id: analysisId });
      if (res.data.success) {
        setWorkflowState('COMPLETED');
        const exec = res.data.execution;
        setOrderStatus({ type: 'success', message: executeMessage(exec) });
      } else {
        setWorkflowState('ERROR');
        setOrderStatus({ type: 'error', message: res.data.error || 'Check failed to execute trade.' });
      }
    } catch (err: any) {
      setWorkflowState('ERROR');
      setOrderStatus({ type: 'error', message: err.message || 'Error confirming trade' });
    }
  };

  const executeMessage = (exec: any) => {
     if (!exec) return "Success.";
     const brokerInf = exec.order_info || {};
     return `Trade executed. Order ID: ${brokerInf.id || brokerInf.order_id || 'Unknown'}. Status: ${brokerInf.status || 'accepted'}`;
  }

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)] w-full flex flex-col items-center pb-[120px]">
      <div className="w-full max-w-xl px-6 pt-[80px] space-y-[40px]">

        {/* BANNER */}
        <div className="bg-[var(--surface-card)] border border-[var(--color-signal-lime)] p-4 flex items-center justify-between">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-signal-lime)]">
            PAPER ONLY
          </div>
          <div className="text-ui-sans text-[11px] uppercase tracking-[0.08em] text-[var(--color-chalk)]">
            Alpaca Simulated Execution
          </div>
        </div>

        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8">
            [ KRONOS WORKFLOW ]
          </div>

          {workflowState === 'IDLE' || workflowState === 'ERROR' ? (
            <form onSubmit={runAgent} className="space-y-[32px]">
              <div className="space-y-[24px]">
                <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                    <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">SYMBOL</label>
                    <input
                       type="text"
                       value={symbol}
                       onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                       placeholder="AAPL..."
                       className="bg-transparent border-none text-right text-code-mono text-[24px] text-[var(--color-chalk)] focus:outline-none w-32 uppercase"
                       required
                    />
                </div>
              </div>
              <button
                 type="submit"
                 disabled={!symbol}
                 className="w-full inline-flex h-[44px] items-center justify-center rounded-[4px] border border-[var(--color-graphite)] px-[32px] text-[14px] font-medium text-[var(--color-chalk)] transition-transform active:scale-95 glow-signal disabled:opacity-50 mt-8 uppercase hover:border-[var(--color-ash)]"
              >
                 RUN AGENT EVALUATION
              </button>
            </form>
          ) : workflowState === 'RUNNING' ? (
             <div className="text-center text-code-mono text-[var(--color-ash)] py-10 animate-pulse">Running KRONOS AI + Risk engines...</div>
          ) : workflowState === 'PENDING_CONFIRMATION' && proposedOrder ? (
            <div className="space-y-[32px]">
              <div className="text-ui-sans text-[14px] text-[var(--color-signal-lime)] mb-4">
                 ⚠️ TRADE PROPOSAL PENDING CONFIRMATION
              </div>
              
              <div className="space-y-[24px]">
                 <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                    <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">SYMBOL</label>
                    <div className="text-code-mono text-[24px] text-[var(--color-chalk)] uppercase">
                       {proposedOrder.symbol}
                    </div>
                 </div>

                 <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                    <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">SIGNAL / SIDE</label>
                    <div className={`text-code-mono text-[24px] ${proposedOrder.side === 'BUY' ? 'text-[var(--color-signal-lime)]' : 'text-[#ff4a4a]'}`}>
                       {proposedOrder.side}
                    </div>
                 </div>

                 <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                    <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">ADJ QUANTITY (RISK CONTROLLED)</label>
                    <div className="text-code-mono text-[24px] text-[var(--color-chalk)]">
                       {proposedOrder.quantity}
                    </div>
                 </div>

                 <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                    <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">MARKET PRICE</label>
                    <div className="text-code-mono text-[20px] text-[var(--color-chalk)]">
                       ${proposedOrder.price?.toFixed(2)}
                    </div>
                 </div>
                 
                 <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                    <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">EST VALUE</label>
                    <div className="text-code-mono text-[20px] text-[var(--color-chalk)]">
                       ${((proposedOrder.price || 0) * (proposedOrder.quantity || 0)).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}
                    </div>
                 </div>

                 {metrics && (
                   <div className="bg-[var(--surface-canvas)] p-4 border border-[var(--color-graphite)] mt-4">
                      <div className="text-ui-sans text-[11px] uppercase text-[var(--color-smoke)] mb-2 tracking-[0.1em]">ACTUAL WALK-FORWARD EVALUATION METRICS</div>
                      <div className="text-ui-sans text-[13px] text-[var(--color-ash)]"><span className="text-[var(--color-chalk)]">MAE:</span> {metrics.MAE}</div>
                      <div className="text-ui-sans text-[13px] text-[var(--color-ash)]"><span className="text-[var(--color-chalk)]">RMSE:</span> {metrics.RMSE}</div>
                      <div className="text-ui-sans text-[13px] text-[var(--color-ash)]"><span className="text-[var(--color-chalk)]">Dir. Accuracy:</span> {metrics.directional_accuracy || 'N/A'}</div>
                   </div>
                 )}
              </div>

              <div className="flex gap-4">
                <button
                   type="button"
                   onClick={() => setWorkflowState('IDLE')}
                   className="w-full inline-flex h-[44px] items-center justify-center rounded-[4px] border border-[var(--color-graphite)] px-[32px] text-[14px] font-medium text-[var(--color-smoke)] transition-transform active:scale-95 mt-8 uppercase hover:bg-[var(--surface-canvas)]"
                >
                   REJECT
                </button>
                <button
                   type="button"
                   onClick={confirmTrade}
                   className="w-full inline-flex h-[44px] items-center justify-center rounded-[4px] bg-[var(--color-signal-lime)] px-[32px] text-[14px] font-medium text-[var(--color-void-black)] transition-transform active:scale-95 glow-signal mt-8 uppercase"
                >
                   CONFIRM PAPER TRADE
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
               <div className="text-center text-[var(--color-chalk)] text-[20px] font-medium py-8">
                  Workflow Completed
               </div>
               <button
                  type="button"
                  onClick={() => setWorkflowState('IDLE')}
                  className="w-full inline-flex h-[44px] items-center justify-center rounded-[4px] border border-[var(--color-graphite)] px-[32px] text-[14px] font-medium text-[var(--color-chalk)] transition-transform active:scale-95 mt-4 uppercase hover:border-[var(--color-ash)]"
               >
                  RUN ANOTHER
               </button>
            </div>
          )}

          {orderStatus.type && (
             <div className={`mt-8 p-4 text-ui-sans text-[11px] uppercase tracking-[0.1em] border ${orderStatus.type === 'success' ? 'border-[var(--color-signal-lime)] text-[var(--color-signal-lime)]' : 'border-[#ff4a4a] text-[#ff4a4a]'}`}>
                {orderStatus.message}
             </div>
          )}
        </section>
      </div>
    </div>
  );
}
