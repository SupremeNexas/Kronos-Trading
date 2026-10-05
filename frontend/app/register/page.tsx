'use client';
import React, { useState } from 'react';
import axios from 'axios';

export default function Register() {
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
    <div className="flex h-screen items-center justify-center bg-gray-900 text-white">
      <div className="p-8 bg-gray-800 rounded shadow-md w-96 border border-gray-700">
        <h2 className="text-2xl font-bold mb-4">Kronos Register</h2>
        <form onSubmit={handleRegister}>
          <div className="mb-4">
            <label className="block text-sm mb-2 text-gray-400">Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} 
                   className="w-full p-2 bg-gray-900 border border-gray-700 rounded text-white" />
          </div>
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
          <button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white p-2 rounded">
            Create Account
          </button>
        </form>
        <div className="mt-4 text-sm text-center">
          <a href="/login" className="text-blue-400 hover:underline">Already have an account? Log In</a>
        </div>
      </div>
    </div>
  );
}
