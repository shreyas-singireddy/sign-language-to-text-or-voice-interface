import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface HistoryItem {
  id: string;
  timestamp: string;
  translatedText: string;
  detectedGesture: string;
}

const languages = ['English', 'Hindi', 'Telugu', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Arabic', 'Portuguese', 'Russian', 'Italian', 'Korean', 'Bengali', 'Tamil', 'Urdu'];

export default function Dashboard() {
  const { user, token } = useAuth();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [prediction, setPrediction] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [status, setStatus] = useState('Idle');
  const [outputText, setOutputText] = useState('');
  const [language, setLanguage] = useState('English');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [speechRate, setSpeechRate] = useState(1);
  const [volume, setVolume] = useState(1);

  useEffect(() => {
    const fetchHistory = async () => {
      const response = await fetch('/api/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        setHistory(await response.json());
      }
    };
    if (token) fetchHistory();
  }, [token]);

  useEffect(() => {
    if (cameraActive && videoRef.current) {
      navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      });
    } else if (!cameraActive && videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach((track) => track.stop());
      if (videoRef.current) videoRef.current.srcObject = null;
    }
  }, [cameraActive]);

  const startCamera = () => setCameraActive(true);
  const stopCamera = () => setCameraActive(false);

  const handleTranslate = async () => {
    if (!videoRef.current) return;
    setStatus('Analyzing...');
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d')?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');

    const response = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ imageData, language })
    });

    if (!response.ok) {
      setStatus('Translation failed');
      return;
    }

    const data = await response.json();
    setPrediction(data.detectedGesture);
    setConfidence(data.confidence);
    setOutputText(data.translatedText);
    setStatus('Recognized');
    setHistory((prev) => [data.record, ...prev]);
  };

  const handleSpeech = () => {
    const utterance = new SpeechSynthesisUtterance(outputText);
    utterance.rate = speechRate;
    utterance.volume = volume;
    const languageMap: Record<string, string> = {
      English: 'en-US',
      Hindi: 'hi-IN',
      Telugu: 'te-IN',
      Spanish: 'es-ES',
      French: 'fr-FR',
      German: 'de-DE',
      Chinese: 'zh-CN',
      Japanese: 'ja-JP',
      Arabic: 'ar-SA',
      Portuguese: 'pt-PT',
      Russian: 'ru-RU',
      Italian: 'it-IT',
      Korean: 'ko-KR',
      Bengali: 'bn-BD',
      Tamil: 'ta-IN',
      Urdu: 'ur-PK'
    };
    utterance.lang = languageMap[language] ?? 'en-US';
    speechSynthesis.speak(utterance);
  };

  const handlePause = () => speechSynthesis.pause();
  const handleStop = () => speechSynthesis.cancel();
  const handleCopy = () => navigator.clipboard.writeText(outputText);
  const handleClear = () => setOutputText('');

  return (
    <div className="space-y-8">
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95 lg:col-span-2">
          <h2 className="text-2xl font-semibold text-slate-950 dark:text-white">Webcam Panel</h2>
          <div className="mt-4 space-y-4">
            <video ref={videoRef} className="h-80 w-full rounded-3xl bg-slate-950 object-cover" muted playsInline />
            <div className="flex flex-wrap gap-3">
              <button onClick={startCamera} className="rounded-full bg-brand-600 px-5 py-2 text-white hover:bg-brand-700">Start Camera</button>
              <button onClick={stopCamera} className="rounded-full border border-slate-300 px-5 py-2 hover:border-brand-500 dark:border-slate-700">Stop Camera</button>
              <button onClick={handleTranslate} className="rounded-full bg-brand-600 px-5 py-2 text-white hover:bg-brand-700">Detect Gesture</button>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">Camera status: {cameraActive ? 'Active' : 'Inactive'}</p>
          </div>
        </div>
        <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
          <h2 className="text-2xl font-semibold text-slate-950 dark:text-white">Recognition Panel</h2>
          <div className="mt-6 space-y-4 text-slate-700 dark:text-slate-200">
            <p><span className="font-semibold">Detected Gesture:</span> {prediction || 'Waiting...'}</p>
            <p><span className="font-semibold">Confidence:</span> {confidence ? `${confidence}%` : '—'}</p>
            <p><span className="font-semibold">Status:</span> {status}</p>
            <p><span className="font-semibold">Current Prediction:</span> {prediction ? `${prediction} detected` : 'No prediction yet'}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
          <h2 className="text-2xl font-semibold text-slate-950 dark:text-white">Translation Output</h2>
          <textarea value={outputText} onChange={(e) => setOutputText(e.target.value)} rows={8} className="mt-4 w-full rounded-3xl border border-slate-300 bg-slate-50 p-4 text-slate-900 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="Translated text will appear here" />
          <div className="mt-4 flex flex-wrap gap-3">
            <button onClick={handleCopy} className="rounded-full bg-slate-800 px-5 py-2 text-white hover:bg-slate-900">Copy Text</button>
            <button onClick={handleClear} className="rounded-full border border-slate-300 px-5 py-2 hover:border-brand-500 dark:border-slate-700">Clear Text</button>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
          <h2 className="text-2xl font-semibold text-slate-950 dark:text-white">Voice Controls</h2>
          <div className="mt-5 space-y-4 text-slate-700 dark:text-slate-200">
            <div>
              <label className="block text-sm font-semibold">Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)} className="mt-2 w-full rounded-3xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
                {languages.map((lang) => <option key={lang} value={lang}>{lang}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold">Speed</label>
              <input type="range" min="0.5" max="2" step="0.1" value={speechRate} onChange={(e) => setSpeechRate(Number(e.target.value))} className="mt-2 w-full" />
            </div>
            <div>
              <label className="block text-sm font-semibold">Volume</label>
              <input type="range" min="0" max="1" step="0.1" value={volume} onChange={(e) => setVolume(Number(e.target.value))} className="mt-2 w-full" />
            </div>
            <div className="flex flex-wrap gap-3">
              <button onClick={handleSpeech} className="rounded-full bg-brand-600 px-5 py-2 text-white hover:bg-brand-700">Play Speech</button>
              <button onClick={handlePause} className="rounded-full border border-slate-300 px-5 py-2 hover:border-brand-500 dark:border-slate-700">Pause Speech</button>
              <button onClick={handleStop} className="rounded-full border border-slate-300 px-5 py-2 hover:border-brand-500 dark:border-slate-700">Stop Speech</button>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-6 shadow-glass backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-slate-950 dark:text-white">Translation History</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Recent translations saved to your account.</p>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-300">Welcome, {user?.name}</p>
        </div>
        <div className="mt-6 space-y-4">
          {history.length === 0 ? (
            <p className="text-slate-600 dark:text-slate-400">No translations yet. Start with the camera panel.</p>
          ) : (
            history.map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-200/80 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/90">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="font-semibold text-slate-950 dark:text-white">{item.detectedGesture}</p>
                  <span className="rounded-full bg-slate-200 px-3 py-1 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300">{new Date(item.timestamp).toLocaleString()}</span>
                </div>
                <p className="mt-2 text-slate-700 dark:text-slate-300">{item.translatedText}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
