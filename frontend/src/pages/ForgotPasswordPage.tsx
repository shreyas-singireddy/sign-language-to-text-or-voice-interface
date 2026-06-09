import { FormEvent, useState } from 'react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');

    await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    setMessage('If the account exists, a reset link has been sent to your email.');
  }

  return (
    <section className="mx-auto max-w-xl rounded-[2rem] border border-slate-200/80 bg-white/90 p-10 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
      <h1 className="text-3xl font-semibold text-slate-950 dark:text-white">Reset your password</h1>
      <p className="mt-3 text-slate-600 dark:text-slate-300">Enter your email address and we will send a secure reset link.</p>
      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        <label className="block">
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Email</span>
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required className="mt-2 w-full rounded-3xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" />
        </label>
        {message && <p className="text-sm text-brand-600 dark:text-brand-300">{message}</p>}
        <button type="submit" className="w-full rounded-full bg-brand-600 px-6 py-3 text-white transition hover:bg-brand-700">Send reset link</button>
      </form>
    </section>
  );
}
