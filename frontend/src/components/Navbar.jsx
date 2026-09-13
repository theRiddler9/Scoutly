import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Menu,
  X,
  Bell,
  Rocket
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/opportunities', label: 'Opportunities' },
  { path: '/applications', label: 'Applications' },
  { path: '/profile', label: 'Profile' },
];

export default function Navbar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b"
           style={{
             background: 'rgba(11, 14, 20, 0.85)',
             borderColor: 'rgba(255, 255, 255, 0.05)',
           }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-105"
                   style={{
                     background: 'linear-gradient(135deg, #4c6ef5, #7048e8)',
                   }}>
                <Rocket className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Scout<span className="text-[#f06595]">ly</span>
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-2">
              {navItems.map(({ path, label }) => {
                const isActive = location.pathname === path;
                return (
                  <Link
                    key={path}
                    to={path}
                    className={`flex items-center gap-2 px-5 py-2 rounded-full text-sm font-medium transition-all duration-300
                      ${isActive
                        ? 'text-white bg-white/5'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                      }`}
                  >
                    {isActive && (
                      <div className="w-1.5 h-1.5 rounded-full bg-[#4c6ef5]" />
                    )}
                    {label}
                  </Link>
                );
              })}
            </div>

            {/* Right Side Actions */}
            <div className="hidden md:flex items-center gap-4">
              <button className="relative p-2 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/5">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#e64980] border border-[#0b0e14]"></span>
              </button>
              <Link to="/profile" className="flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-br from-[#7048e8] to-[#f06595] text-white text-sm font-semibold hover:opacity-90 transition-opacity">
                AJ
              </Link>
            </div>

            {/* Mobile Toggle */}
            <div className="flex md:hidden items-center gap-4">
              <button className="relative p-2 text-gray-400 hover:text-white">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#e64980] border border-[#0b0e14]"></span>
              </button>
              <button
                className="p-2 rounded-lg text-gray-400 hover:text-white transition-colors"
                onClick={() => setMobileOpen(!mobileOpen)}
              >
                {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <div className="md:hidden border-t animate-slide-up"
               style={{
                 borderColor: 'rgba(255, 255, 255, 0.05)',
                 background: 'rgba(11, 14, 20, 0.95)',
               }}>
            <div className="px-4 py-4 space-y-2">
              {navItems.map(({ path, label }) => {
                const isActive = location.pathname === path;
                return (
                  <Link
                    key={path}
                    to={path}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300
                      ${isActive ? 'text-white bg-white/5' : 'text-gray-400'}`}
                  >
                    {isActive && (
                      <div className="w-1.5 h-1.5 rounded-full bg-[#4c6ef5]" />
                    )}
                    {label}
                  </Link>
                );
              })}
              <div className="pt-4 border-t border-white/5 flex items-center gap-3 px-4">
                 <div className="flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-br from-[#7048e8] to-[#f06595] text-white text-sm font-semibold">
                  AJ
                </div>
                <span className="text-gray-300 font-medium">Akash</span>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Spacer */}
      <div className="h-20" />
    </>
  );
}
