import re

with open('frontend/app/profile/page.tsx', 'r') as f:
    content = f.read()

react_imports = "import React, { useEffect, useState } from 'react';"
if "import React, { useEffect, useState } from 'react';" in content:
    pass

state_hooks = """
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
"""
content = re.sub(r'const \[user, setUser\] = useState<any>\(null\);\n  const \[acc, setAcc\] = useState<any>\(null\);', state_hooks.strip(), content)

ui_render = """
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
"""
content = re.sub(r'\{/\* Edit functionality might be limited here.*?</button>\n         </div>', ui_render.strip() + '\n         </div>', content, flags=re.DOTALL)

with open('frontend/app/profile/page.tsx', 'w') as f:
    f.write(content)

