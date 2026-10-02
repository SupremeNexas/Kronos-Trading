'use client';

import React, { useState } from 'react';
import { placeOrder } from '@/lib/api';

export default function PaperTradingPage() {
  const [orderForm, setOrderForm] = useState({
    symbol: '',
    side: 'BUY',
    quantity: '',
    price: ''
  });

  const [orderStatus, setOrderStatus] = useState<{type: 'success' | 'error' | null, message: string}>({type: null, message: ''});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOrderSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setOrderStatus({ type: null, message: '' });

    if (!orderForm.symbol) return setOrderStatus({ type: 'error', message: 'Symbol is required' });
    const qty = Number(orderForm.quantity);
    if (isNaN(qty) || qty <= 0) return setOrderStatus({ type: 'error', message: 'Quantity must be greater than 0' });

    setIsSubmitting(true);
    try {
      const orderPayload = {
        symbol: orderForm.symbol.toUpperCase(),
        side: orderForm.side,
        quantity: qty,
        order_type: 'MARKET',
        price: 0
      };

      const res = await placeOrder(orderPayload);
      if (res.data?.success || res.data?.success) {
        setOrderStatus({ type: 'success', message: `Order placed: ${orderPayload.side} ${qty} ${orderPayload.symbol}` });
        setOrderForm({ symbol: '', side: 'BUY', quantity: '', price: '' });
      } else {
        setOrderStatus({ type: 'error', message: res.data?.error || res.data?.error || 'Failed to place order' });
      }
    } catch (err: any) {
      setOrderStatus({ type: 'error', message: err.message || 'An error occurred while placing the order' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const estPrice = Number(orderForm.price) || 0;
  const quantity = Number(orderForm.quantity) || 0;
  const estValue = estPrice * quantity;

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
            [ PAPER EXECUTION ]
          </div>

          <form onSubmit={handleOrderSubmit} className="space-y-[32px]">
            <div className="space-y-[24px]">
               <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                  <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">SYMBOL</label>
                  <input
                     type="text"
                     value={orderForm.symbol}
                     onChange={(e) => setOrderForm({...orderForm, symbol: e.target.value.toUpperCase()})}
                     placeholder="AAPL..."
                     className="bg-transparent border-none text-right text-code-mono text-[24px] text-[var(--color-chalk)] focus:outline-none w-32 uppercase"
                     required
                  />
               </div>

               <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                  <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">SIGNAL</label>
                  <div className="flex space-x-2">
                     <button
                        type="button"
                        onClick={() => setOrderForm({...orderForm, side: 'BUY'})}
                        className={`text-ui-sans text-[11px] tracking-[0.1em] font-medium border px-4 py-1 inline-block ${orderForm.side === 'BUY' ? 'border-[var(--color-signal-lime)] text-[var(--color-signal-lime)]' : 'border-[var(--color-graphite)] text-[var(--color-smoke)]'}`}
                     >
                        BUY
                     </button>
                     <button
                        type="button"
                        onClick={() => setOrderForm({...orderForm, side: 'SELL'})}
                        className={`text-ui-sans text-[11px] tracking-[0.1em] font-medium border px-4 py-1 inline-block ${orderForm.side === 'SELL' ? 'border-[var(--color-chalk)] text-[var(--color-chalk)]' : 'border-[var(--color-graphite)] text-[var(--color-smoke)]'}`}
                     >
                        SELL
                     </button>
                  </div>
               </div>

               <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                  <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">QUANTITY</label>
                  <input
                     type="number"
                     value={orderForm.quantity}
                     onChange={(e) => setOrderForm({...orderForm, quantity: e.target.value})}
                     placeholder="10"
                     className="bg-transparent border-none text-right text-code-mono text-[24px] text-[var(--color-chalk)] focus:outline-none w-32"
                     required
                  />
               </div>

               <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                  <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">EST. PRICE</label>
                  <input
                     type="number"
                     step="0.01"
                     value={orderForm.price}
                     onChange={(e) => setOrderForm({...orderForm, price: e.target.value})}
                     placeholder="0.00"
                     className="bg-transparent border-none text-right text-code-mono text-[20px] text-[var(--color-chalk)] focus:outline-none w-32"
                  />
               </div>

               <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                  <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">EST. VALUE</label>
                  <div className="text-code-mono text-[20px] text-[var(--color-chalk)]">${estValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
               </div>

               <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                  <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">RISK</label>
                  <div className="text-code-mono text-[20px] text-[var(--color-ash)]">2.00%</div>
               </div>
            </div>

            <button
               type="submit"
               disabled={isSubmitting || !orderForm.symbol || !orderForm.quantity}
               className="w-full inline-flex h-[44px] items-center justify-center rounded-[4px] bg-[var(--color-signal-lime)] px-[32px] text-[14px] font-medium text-[var(--color-void-black)] transition-transform active:scale-95 glow-signal disabled:opacity-50 mt-8 uppercase"
            >
               {isSubmitting ? 'SUBMITTING...' : 'CONFIRM PAPER TRADE'}
            </button>

            {orderStatus.type && (
               <div className={`mt-4 p-4 text-ui-sans text-[11px] uppercase tracking-[0.1em] border ${orderStatus.type === 'success' ? 'border-[var(--color-signal-lime)] text-[var(--color-signal-lime)]' : 'border-[#ff4a4a] text-[#ff4a4a]'}`}>
                  {orderStatus.message}
               </div>
            )}
          </form>
        </section>
      </div>
    </div>
  );
}