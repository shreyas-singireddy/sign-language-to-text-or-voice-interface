import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200/80 bg-white/80 py-8 text-slate-600 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80 dark:text-slate-400">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 sm:px-6 lg:px-8 lg:flex-row lg:items-center lg:justify-between">
        <p className="text-sm">© 2026 SignBridge AI. Built for accessible communication.</p>
        <div className="flex flex-wrap gap-4 text-sm">
          <Link to="/" className="hover:text-brand-600">About</Link>
          <Link to="/" className="hover:text-brand-600">Privacy</Link>
          <Link to="/" className="hover:text-brand-600">Terms</Link>
          <Link to="/" className="hover:text-brand-600">Contact</Link>
        </div>
      </div>
    </footer>
  );
}
