interface StatsCardProps {
  stat: string;
  label: string;
}

export default function StatsCard({ stat, label }: StatsCardProps) {
  return (
    <div className="rounded-3xl border border-slate-200/80 bg-white/80 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
      <p className="text-4xl font-semibold text-brand-600 dark:text-brand-400">{stat}</p>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{label}</p>
    </div>
  );
}
