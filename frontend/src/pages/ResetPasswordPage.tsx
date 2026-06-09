import { FormEvent, useState } from 'react';

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');

    await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });

    setMessage('Your password has been updated successfully.');
  }

  return (
    <section className="mx-auto max-w-xl rounded-[2rem] border border-slate-200/80 bg-white/90 p-10 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
      <h1 className="text-3xl font-semibold text-slate-950 dark:text-white">Choose a new password</h1>
      <p className="mt-3 text-slate-600 dark:text-slate-300">Enter a new secure password to restore access to your account.</p>
      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        <label className="block">
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">New Password</span>
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required className="mt-2 w-full rounded-3xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" />
        </label>
        {message && <p className="text-sm text-brand-600 dark:text-brand-300">{message}</p>}
        <button type="submit" className="w-full rounded-full bg-brand-600 px-6 py-3 text-white transition hover:bg-brand-700">Update password</button>
      </form>
    </section>
  );
}
