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
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/auth/login', { email, password }, { withCredentials: true });
      if (res.data.success) {
         window.location.href = '/dashboard';
      }
    } catch(err: any) {
      alert(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900 border-gray-800 text-white">
      <div className="p-8 bg-gray-800 rounded shadow-md w-96 border border-gray-700">
        <h2 className="text-2xl font-bold mb-4">Kronos Login</h2>
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-sm mb-2 text-gray-400">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} 
                   className="w-full p-2 bg-gray-900 border border-gray-700 rounded text-white" />
          </div>
          <div className="mb-4">
            <label className="block text-sm mb-2 text-gray-400">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} 
                   className="w-full p-2 bg-gray-900 border border-gray-700 rounded text-white" />
          </div>
          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded">
            Log In
          </button>
        </form>
        <div className="mt-4 text-sm text-center">
          <a href="/register" className="text-blue-400 hover:underline">Create an account</a>
        </div>
      </div>
    </div>
  );
}
