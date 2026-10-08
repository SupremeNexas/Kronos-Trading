'use client';
import React, { useState } from 'react';
import axios from 'axios';

export default function Register() {
  React.useEffect(() => {
    if (process.env.NEXT_PUBLIC_LOCAL_TRADING_MODE === 'true') {
      window.location.href = '/dashboard';
    }
  }, []);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/auth/register', { email, password, name }, { withCredentials: true });
      if (res.data.success) {
         window.location.href = '/dashboard';
      }
    } catch(err: any) {
      let errMsg = "Registration failed";
      if (err.response && err.response.data) {
        if (typeof err.response.data.error === 'string') {
          errMsg = err.response.data.error;
        } else if (typeof err.response.data === 'string') {
          errMsg = err.response.data;
        } else {
          errMsg = JSON.stringify(err.response.data);
        }
      } else if (err.message) {
        errMsg = err.message;
      }
      alert(errMsg);
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
             Create <span className="italic text-[var(--color-signal-lime)]">Account.</span>
          </h2>
          
          <form onSubmit={handleRegister} className="space-y-[32px]">
            <div className="space-y-[24px]">
              <div className="flex justify-between items-center border-b border-[var(--color-graphite)] pb-4">
                <label className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)]">NAME</label>
                <input type="text" value={name} onChange={e => setName(e.target.value)} 
                       className="bg-transparent border-none text-right text-code-mono text-[16px] text-[var(--color-chalk)] focus:outline-none w-48" required placeholder="Jane Doe" />
              </div>
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
              REGISTER
            </button>
          </form>
          <div className="mt-8 text-center border-t border-[var(--color-graphite)] pt-6">
            <a href="/login" className="text-ui-sans text-[11px] uppercase tracking-[0.18em] text-[var(--color-smoke)] hover:text-[var(--color-chalk)] transition-colors">Already have an account? Log In</a>
          </div>
        </section>
      </div>
    </div>
  );
}
