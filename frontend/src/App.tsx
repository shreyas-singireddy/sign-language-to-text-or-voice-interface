import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function Home() {
  return (
    <div className="min-h-screen flex flex-col justify-between">
      <header className="border-b border-slate-200/80 bg-white/80 py-4 px-6 dark:border-slate-800 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold">S</div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-brand-600 to-indigo-600 bg-clip-text text-transparent">SignBridge AI</span>
          </div>
          <nav className="flex gap-4">
            <Link to="/" className="text-sm font-medium text-slate-600 hover:text-brand-600 transition dark:text-slate-300 dark:hover:text-brand-400">Home</Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-3xl w-full text-center space-y-6">
          <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-6xl">
            Welcome to <span className="bg-gradient-to-r from-brand-600 to-indigo-600 bg-clip-text text-transparent">SignBridge AI</span>
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            An AI-powered communication platform designed to translate sign language into text and speech in real time.
          </p>
          <div className="pt-4">
            <div className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-full bg-slate-100 text-slate-800 text-sm font-semibold dark:bg-slate-800 dark:text-slate-200 border border-slate-200/50 dark:border-slate-700/50">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Boilerplate Ready & Connected
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200/80 py-6 px-6 dark:border-slate-800 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto text-center text-xs text-slate-500">
          &copy; {new Date().getFullYear()} SignBridge AI. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}
