import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Opportunities from './pages/Opportunities';
import Applications from './pages/Applications';

export default function App() {
  return (
    <BrowserRouter>
      {/* Background mesh effect */}
      <div className="bg-mesh" />

      <Navbar />

      <main className="relative z-10">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/opportunities" element={<Opportunities />} />
          <Route path="/applications" element={<Applications />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t mt-16 py-6 text-center"
              style={{ borderColor: 'rgba(255, 255, 255, 0.04)' }}>
        <p className="text-xs text-gray-500">
          Powered by <span className="font-semibold text-gray-400">Qwen</span> & <span className="font-semibold text-gray-400">Playwright</span>
        </p>
      </footer>
    </BrowserRouter>
  );
}
