interface FeatureCardProps {
  title: string;
  description: string;
}

export default function FeatureCard({ title, description }: FeatureCardProps) {
  return (
    <article className="rounded-3xl border border-slate-200/80 bg-white/80 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
      <h3 className="text-xl font-semibold text-slate-900 dark:text-white">{title}</h3>
      <p className="mt-3 text-slate-600 dark:text-slate-300">{description}</p>
    </article>
  );
}
