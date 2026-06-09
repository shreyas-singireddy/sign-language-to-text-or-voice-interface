import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import FeatureCard from '../components/FeatureCard';
import StatsCard from '../components/StatsCard';
import FAQAccordion from '../components/FAQAccordion';
import LiveFeed from '../components/LiveFeed';

const features = [
  { title: 'Real-Time Recognition', description: 'Live gesture analysis with webcam input and instant translation.' },
  { title: 'AI Translation', description: 'Powerful AI detects ASL signs and maps them to text and speech.' },
  { title: 'Voice Output', description: 'Automatically convert recognized gestures into spoken audio.' },
  { title: 'Accessibility Focused', description: 'Designed for inclusive communication with screen readers and keyboard navigation.' },
  { title: 'Multi-Language Support', description: 'Translate output across English, Hindi, Telugu, Spanish, and French.' },
  { title: 'Translation History', description: 'Save and manage previous translations securely from your dashboard.' }
];

const testimonials = [
  { name: 'Priya Sharma', quote: 'SignBridge AI helped my family communicate much faster with our neighbors.', role: 'Community Advocate' },
  { name: 'Jordan Lee', quote: 'The live translation dashboard is intuitive, responsive, and beautifully designed.', role: 'Accessibility Lead' },
  { name: 'Maya Patel', quote: 'I love the dark mode and the way the platform keeps translation history safe.', role: 'User Experience Designer' }
];

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <section className="space-y-20">
      <div className="grid gap-10 rounded-[2rem] border border-slate-200/70 bg-white/90 p-10 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/90 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-600">Breaking Communication Barriers</p>
          <h1 className="max-w-3xl text-5xl font-bold tracking-tight text-slate-950 dark:text-white sm:text-6xl">
            Breaking Communication Barriers with AI
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
            Translate American Sign Language into text and voice in real time. Built for accessibility, responsiveness, and modern interactions.
          </p>
          <div className="flex flex-wrap gap-4">
            <button onClick={() => navigate('/dashboard')} className="rounded-full bg-brand-600 px-6 py-3 text-white shadow-lg shadow-brand-500/10 transition hover:bg-brand-700">
              Start Translating
            </button>
            <button onClick={() => window.alert('Demo coming soon')} className="rounded-full border border-slate-300 px-6 py-3 text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-100 dark:hover:bg-slate-800">
              Watch Demo
            </button>
          </div>
        </div>
        <div className="rounded-[2rem] bg-slate-100 p-8 shadow-glass dark:bg-slate-950/95">
          <div className="space-y-4 rounded-[1.75rem] border border-slate-200/80 bg-white/90 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/90">
            <div className="rounded-3xl bg-brand-500/10 p-6 text-brand-600 dark:bg-brand-500/10 dark:text-brand-200">
              <p className="text-sm font-semibold uppercase tracking-[0.24em]">Live flow</p>
              <div className="mt-6 space-y-5 text-slate-700 dark:text-slate-200">
                <p>Webcam → Hand Gesture Detection → AI Recognition → Text Output → Voice Output</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {features.map((feature) => (
          <FeatureCard key={feature.title} title={feature.title} description={feature.description} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <StatsCard stat="99%" label="Accuracy" />
        <StatsCard stat="Real-Time" label="Processing" />
        <StatsCard stat="A11y" label="Accessibility Focused" />
        <StatsCard stat="5+" label="Languages" />
        <StatsCard stat="Safe" label="Privacy Ready" />
      </div>

      <LiveFeed />

      <div className="grid gap-8 lg:grid-cols-3">
        {testimonials.map((testimonial) => (
          <div key={testimonial.name} className="rounded-3xl border border-slate-200/80 bg-white/80 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
            <p className="text-lg leading-8 text-slate-700 dark:text-slate-200">“{testimonial.quote}”</p>
            <p className="mt-5 font-semibold text-slate-900 dark:text-white">{testimonial.name}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">{testimonial.role}</p>
          </div>
        ))}
      </div>

      <div className="rounded-[2rem] border border-slate-200/70 bg-white/80 p-8 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
        <h2 className="text-3xl font-semibold text-slate-950 dark:text-white">FAQ</h2>
        <p className="mt-2 text-slate-600 dark:text-slate-300">Common questions about how SignBridge AI works and how to get started.</p>
        <FAQAccordion />
      </div>
    </section>
  );
}
