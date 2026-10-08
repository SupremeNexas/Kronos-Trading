'use client';
import React, { useState } from 'react';
import axios from 'axios';

export default function Login() {
  React.useEffect(() => {
    if (process.env.NEXT_PUBLIC_LOCAL_TRADING_MODE === 'true') {
      window.location.href = '/dashboard';
    }
  }, []);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/auth/login', { email, password }, { withCredentials: true });
      if (res.data.success) {
         window.location.href = '/dashboard';
      }
    } catch(err: any) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-[var(--surface-canvas)] w-full pb-[120px]">
      <div className="w-full max-w-sm px-6">
        <section className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-[40px]">
          <div className="text-ui-sans text-[11px] font-medium uppercase tracking-[0.22em] text-[var(--color-ash)] mb-8 text-center">
            [ SECURE ACCESS ]
          </div>
          <h2 className="text-display-serif font-light text-[32px] leading-tight tracking-[-1px] text-[var(--color-chalk)] mb-8 text-center">
             System <span className="italic text-[var(--color-signal-lime)]">Login.</span>
          </h2>
          
          <form onSubmit={handleLogin} className="space-y-[32px]">
            {error && (
               <div className="text-ui-sans text-[11px] tracking-[0.2em] text-[#ff4a4a] uppercase border border-[#ff4a4a] px-4 py-2 mt-4 text-center">
                 {error}
               </div>
            )}
            <div className="space-y-[24px]">
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">EMAIL</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} 
                       className="bg-transparent border-none text-right text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none w-48" required placeholder="user@domain.com" />
              </div>
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">SECRET</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} 
                       className="bg-transparent border-none text-right text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none w-48" required placeholder="••••••••" />
              </div>
            </div>
            <button type="submit" className="w-full inline-flex h-[44px] items-center justify-center rounded-[4px] bg-[var(--color-signal-lime)] px-[32px] text-[14px] font-medium text-[var(--color-void-black)] transition-transform active:scale-95 glow-signal uppercase">
              AUTHENTICATE
            </button>
          </form>
          <div className="mt-8 text-center border-t border-[var(--color-graphite)] pt-6">
            <a href="/register" className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] hover:text-[var(--color-chalk)] transition-colors">Create an account</a>
          </div>
        </section>
      </div>
    </div>
  );
}
