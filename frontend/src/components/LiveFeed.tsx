import { useEffect, useState } from 'react';

interface LiveItem {
  id: string;
  title: string;
  description: string;
}

export default function LiveFeed() {
  const [items, setItems] = useState<LiveItem[]>([]);
  const [source, setSource] = useState('offline');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function fetchLiveData() {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/live-data');
      if (!response.ok) {
        throw new Error('Unable to fetch live data');
      }

      const data = await response.json();
      setItems(data.items || []);
      setSource(data.source || 'offline');
    } catch (err) {
      setError('Unable to load live updates. Showing fallback content.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLiveData();
    const interval = window.setInterval(fetchLiveData, 30000);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-8 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-950 dark:text-white">Live Data Feed</h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Showing real-time content from the web when available, with offline fallback data otherwise.
          </p>
        </div>
        <span className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold uppercase text-slate-600 dark:border-slate-700 dark:text-slate-300">
          {loading ? 'Loading...' : source === 'online' ? 'Online' : 'Offline'}
        </span>
      </div>

      {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {items.length === 0 ? (
          <div className="rounded-3xl border border-slate-200/80 bg-slate-50 p-6 text-slate-700 dark:border-slate-800 dark:bg-slate-950/90 dark:text-slate-200">
            {loading ? 'Loading live updates…' : 'No live updates available right now.'}
          </div>
        ) : (
          items.map((item) => (
            <div key={item.id} className="rounded-3xl border border-slate-200/80 bg-slate-50 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950/90">
              <p className="font-semibold text-slate-950 dark:text-white">{item.title}</p>
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{item.description}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
