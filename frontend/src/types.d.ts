export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  createdAt: string;
}

export interface TranslationRecord {
  id: string;
  userId: string;
  detectedGesture: string;
  translatedText: string;
  confidence: number;
  timestamp: string;
}

export interface AuthState {
  user: UserProfile | null;
  token: string | null;
}
