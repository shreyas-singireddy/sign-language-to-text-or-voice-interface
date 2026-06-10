import { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { UserProfile } from '../types';

interface AuthContextValue {
  user: UserProfile | null;
  token: string | null;
  signIn: (user: UserProfile, token: string) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('signbridge-auth');
    if (stored) {
      const parsed = JSON.parse(stored);
      setUser(parsed.user);
      setToken(parsed.token);
    }
  }, []);

  useEffect(() => {
    if (user && token) {
      localStorage.setItem('signbridge-auth', JSON.stringify({ user, token }));
    } else {
      localStorage.removeItem('signbridge-auth');
    }
  }, [user, token]);

  const signIn = (profile: UserProfile, authToken: string) => {
    setUser(profile);
    setToken(authToken);
  };

  const signOut = () => {
    setUser(null);
    setToken(null);
  };

  return <AuthContext.Provider value={{ user, token, signIn, signOut }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}