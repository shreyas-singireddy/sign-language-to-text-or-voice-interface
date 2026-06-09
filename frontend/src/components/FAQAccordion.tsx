import { useState } from 'react';

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: 'How accurate is the sign language recognition?',
    answer: 'SignBridge AI is designed to deliver reliable results with high confidence scoring for supported gestures and letters.'
  },
  {
    question: 'Which languages can I translate to?',
    answer: 'The platform supports English, Hindi, Telugu, Spanish, and French for translation output.'
  },
  {
    question: 'Do I need an account to start translating?',
    answer: 'Yes. Registration is required to save translation history and access the dashboard securely.'
  }
];

export default function FAQAccordion() {
  const [activeIndex, setActiveIndex] = useState<number | null>(0);

  return (
    <div className="space-y-4">
      {faqs.map((item, index) => (
        <div key={item.question} className="rounded-3xl border border-slate-200/80 bg-white/80 p-5 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
          <button
            type="button"
            onClick={() => setActiveIndex(activeIndex === index ? null : index)}
            className="flex w-full items-center justify-between text-left text-lg font-semibold text-slate-900 dark:text-white"
          >
            {item.question}
            <span className="text-brand-500">{activeIndex === index ? '−' : '+'}</span>
          </button>
          {activeIndex === index && <p className="mt-4 text-slate-600 dark:text-slate-300">{item.answer}</p>}
        </div>
      ))}
    </div>
  );
}
