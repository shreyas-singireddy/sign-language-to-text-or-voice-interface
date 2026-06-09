import StatsCard from '../components/StatsCard';

export default function AdminDashboard() {
  return (
    <div className="space-y-8">
      <div className="grid gap-6 lg:grid-cols-4">
        <StatsCard stat="1.2k" label="Total Users" />
        <StatsCard stat="4.8k" label="Total Translations" />
        <StatsCard stat="87%" label="Active Users" />
        <StatsCard stat="24h" label="Daily Usage" />
      </div>
      <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-8 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
        <h1 className="text-3xl font-semibold text-slate-950 dark:text-white">Admin Analytics</h1>
        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl border border-slate-200/80 bg-slate-50 p-6 dark:border-slate-800 dark:bg-slate-950/95">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">User Management</h2>
            <p className="mt-3 text-slate-600 dark:text-slate-300">Search, filter, and manage accounts with admin controls.</p>
          </div>
          <div className="rounded-3xl border border-slate-200/80 bg-slate-50 p-6 dark:border-slate-800 dark:bg-slate-950/95">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Translation Logs</h2>
            <p className="mt-3 text-slate-600 dark:text-slate-300">Review live history and export translation analytics securely.</p>
          </div>
          <div className="rounded-3xl border border-slate-200/80 bg-slate-50 p-6 dark:border-slate-800 dark:bg-slate-950/95">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Activity Charts</h2>
            <p className="mt-3 text-slate-600 dark:text-slate-300">Monitor usage patterns and accuracy analytics in real time.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
