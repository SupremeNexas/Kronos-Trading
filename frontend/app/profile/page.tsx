'use client';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Profile() {
  const [user, setUser] = useState<any>(null);
  const [acc, setAcc] = useState<any>(null);
  const [newPassword, setNewPassword] = useState('');
  const [isChangingPwd, setIsChangingPwd] = useState(false);

  const changePassword = async () => {
     if (!newPassword || newPassword.length < 6) return alert('Min 6 chars');
     try {
       const res = await axios.patch('/api/profile', { password: newPassword }, { withCredentials: true });
       if (res.data.success) {
          alert('Password updated');
          setIsChangingPwd(false);
          setNewPassword('');
       }
     } catch (e: any) {
       alert(e.response?.data?.error || 'Failed');
     }
  };

  useEffect(() => {
    async function load() {
      try {
        const uRes = await axios.get('/api/auth/me', { withCredentials: true });
        setUser(uRes.data.user);
        const aRes = await axios.get('/api/trading/account', { withCredentials: true });
        setAcc(aRes.data);
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  if (!user) return <div className="p-8 text-white">Loading...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto text-[var(--color-chalk)] space-y-8">
      <h1 className="text-3xl font-light font-serif">Personal Profile</h1>
      
      <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
         <h2 className="text-xl mb-4 font-mono">ACCOUNT DETAILS</h2>
         <div className="space-y-4 text-sm">
            <div className="flex gap-4">
              <div className="w-16 h-16 rounded-full bg-[var(--color-signal-lime)]/20 text-[var(--color-signal-lime)] flex items-center justify-center text-2xl font-bold">
                 {user.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="font-bold text-lg">{user.name}</p>
                <p className="text-[var(--color-ash)]">{user.email}</p>
                <span className="text-[10px] bg-gray-800 px-2 py-1 rounded inline-block mt-1 uppercase border border-gray-700">{user.role}</span>
              </div>
            </div>
            <p>Member Since: {user.created_at}</p>
         </div>
         <div className="mt-6 flex gap-4">
           {/* Edit functionality might be limited here to display only based on prompt request, but let's add dummy buttons */}
           <button className="px-4 py-2 border border-[var(--color-graphite)] text-xs hover:bg-[var(--surface-hover)]">EDIT PROFILE</button>
           <button onClick={() => setIsChangingPwd(!isChangingPwd)} className="px-4 py-2 border border-[var(--color-graphite)] text-xs hover:bg-[var(--surface-hover)]">CHANGE PASSWORD</button>
           <button onClick={async () => { await axios.post('/api/auth/logout', {}, { withCredentials: true }); window.location.href='/login'; }} className="px-4 py-2 bg-red-900/20 text-red-400 border border-red-900/50 text-xs hover:bg-red-900/40">LOGOUT</button>
         </div>
         {isChangingPwd && (
           <div className="mt-4 flex gap-2">
             <input type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="New Password" className="bg-transparent border border-[var(--color-graphite)] px-2 py-1 text-sm outline-none" />
             <button onClick={changePassword} className="px-3 py-1 bg-[var(--color-signal-lime)]/20 text-[var(--color-signal-lime)] border border-[var(--color-signal-lime)]/50 hover:bg-[var(--color-signal-lime)]/30 text-xs text-bold">SAVE</button>
           </div>
         )}
         </div>
      </div>

      <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
         <h2 className="text-xl mb-4 font-mono">PAPER TRADING STATUS</h2>
         {acc ? (
             <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-[var(--color-smoke)] mb-1">Equity</div>
                  <div className="font-mono text-lg">${Number(acc.equity || 0).toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-[var(--color-smoke)] mb-1">Cash</div>
                  <div className="font-mono text-lg">${Number(acc.cash || 0).toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-[var(--color-smoke)] mb-1">Buying Power</div>
                  <div className="font-mono text-lg">${Number(acc.buying_power || 0).toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-[var(--color-smoke)] mb-1">Status</div>
                  <div className="font-mono text-lg text-green-400">{acc.status}</div>
                </div>
             </div>
         ) : <p>Loading Alpaca status...</p>}
      </div>

      <div className="bg-[var(--surface-card)] border border-[var(--color-graphite)] p-6">
         <h2 className="text-xl mb-4 font-mono">ACTIVITY SUMMARY</h2>
         <p className="text-[var(--color-smoke)] text-sm mb-4">Detailed activity history available via specific metrics endpoints.</p>
         <div className="flex gap-4">
            <a href="/trades" className="px-4 py-2 border border-[var(--color-signal-lime)] text-[var(--color-signal-lime)] text-xs bg-[var(--color-signal-lime)]/10 hover:bg-[var(--color-signal-lime)]/20 transition-all">VIEW TRADES</a>
            <a href="/my-stocks" className="px-4 py-2 border border-[var(--color-graphite)] text-xs hover:bg-[var(--surface-hover)]">MY STOCKS</a>
         </div>
      </div>
    </div>
  );
}
