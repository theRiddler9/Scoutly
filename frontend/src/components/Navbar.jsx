import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  FileText,
  User,
  Rocket,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/opportunities', label: 'Opportunities', icon: Search },
  { path: '/applications', label: 'Applications', icon: FileText },
  { path: '/profile', label: 'Profile', icon: User },
];

export default function Navbar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b"
           style={{
             background: 'rgba(13, 15, 31, 0.85)',
             borderColor: 'rgba(255, 255, 255, 0.06)',
           }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                   style={{
                     background: 'linear-gradient(135deg, #4c6ef5, #7048e8)',
                     boxShadow: '0 2px 12px rgba(76, 110, 245, 0.3)',
                   }}>
                <Rocket className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold tracking-tight">
                <span className="gradient-text">Scoutly</span>
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
                    style={{
                      background: 'rgba(240, 101, 149, 0.15)',
                      color: '#f06595',
                      border: '1px solid rgba(240, 101, 149, 0.2)',
                    }}>
                <Sparkles className="w-3 h-3" /> AI
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map(({ path, label, icon: Icon }) => {
                const isActive = location.pathname === path;
                return (
                  <Link
                    key={path}
                    to={path}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300
                      ${isActive
                        ? 'text-white'
                        : 'text-gray-400 hover:text-gray-200'
                      }`}
                    style={isActive ? {
                      background: 'rgba(76, 110, 245, 0.15)',
                      borderColor: 'rgba(76, 110, 245, 0.2)',
                    } : {}}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                );
              })}
            </div>

            {/* Mobile Toggle */}
            <button
              className="md:hidden p-2 rounded-lg text-gray-400 hover:text-white transition-colors"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <div className="md:hidden border-t animate-slide-up"
               style={{
                 borderColor: 'rgba(255, 255, 255, 0.06)',
                 background: 'rgba(13, 15, 31, 0.95)',
               }}>
            <div className="px-4 py-3 space-y-1">
              {navItems.map(({ path, label, icon: Icon }) => {
                const isActive = location.pathname === path;
                return (
                  <Link
                    key={path}
                    to={path}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300
                      ${isActive ? 'text-white' : 'text-gray-400'}`}
                    style={isActive ? { background: 'rgba(76, 110, 245, 0.15)' } : {}}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Spacer */}
      <div className="h-16" />
    </>
  );
}
