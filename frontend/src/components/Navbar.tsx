import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const activeClass = 'text-brand-600 dark:text-white';

export default function Navbar() {
  const { user, signOut } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    signOut();
    navigate('/login');
  };

  return (
    <header className="border-b border-slate-200/70 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="text-lg font-semibold tracking-tight text-slate-900 dark:text-white">
          SignBridge AI
        </Link>
        <nav className="flex items-center gap-4 text-sm font-medium text-slate-600 dark:text-slate-300">
          <NavLink to="/" className={({ isActive }) => (isActive ? activeClass : undefined)}>
            Home
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => (isActive ? activeClass : undefined)}>
            Dashboard
          </NavLink>
          <NavLink to="/admin" className={({ isActive }) => (isActive ? activeClass : undefined)}>
            Admin
          </NavLink>
          <button
            type="button"
            onClick={toggleTheme}
            className="rounded-full border border-slate-200 bg-white px-3 py-1 text-slate-700 shadow-sm transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
          >
            {isDark ? 'Light' : 'Dark'}
          </button>
          {user ? (
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-full bg-brand-500 px-3 py-1 text-white shadow-sm hover:bg-brand-600"
            >
              Sign out
            </button>
          ) : (
            <Link className="rounded-full bg-slate-100 px-3 py-1 text-slate-700 shadow-sm hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100" to="/login">
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
