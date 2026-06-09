import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="mx-auto max-w-3xl rounded-[2rem] border border-slate-200/80 bg-white/90 p-12 text-center shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
      <h1 className="text-5xl font-bold text-slate-950 dark:text-white">404</h1>
      <p className="mt-4 text-xl text-slate-700 dark:text-slate-300">Page not found</p>
      <Link to="/" className="mt-8 inline-flex rounded-full bg-brand-600 px-6 py-3 text-white hover:bg-brand-700">Return home</Link>
    </div>
  );
}
