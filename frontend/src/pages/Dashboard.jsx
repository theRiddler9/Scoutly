import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Target,
  Clock,
  Send,
  TrendingUp,
  ArrowRight,
  Zap,
  Radar,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { dashboardApi, discoveryApi, opportunitiesApi } from '../services/api';
import ScoreRing from '../components/ScoreRing';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentOpps, setRecentOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [matching, setMatching] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, oppsRes] = await Promise.all([
        dashboardApi.getStats(),
        opportunitiesApi.list({ sort_by: 'score', limit: 5 }),
      ]);
      setStats(statsRes.data);
      setRecentOpps(oppsRes.data.opportunities || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const runDiscovery = async () => {
    setDiscovering(true);
    try {
      await discoveryApi.run();
      await loadData();
    } catch (err) {
      console.error('Discovery failed:', err);
    } finally {
      setDiscovering(false);
    }
  };

  const runMatching = async () => {
    setMatching(true);
    try {
      await opportunitiesApi.triggerMatch({ profile_id: 1 });
      await loadData();
    } catch (err) {
      console.error('Matching failed:', err);
    } finally {
      setMatching(false);
    }
  };

  const clearAll = async () => {
    if (confirm('Are you sure you want to clear all discovered opportunities? This cannot be undone.')) {
      try {
        await opportunitiesApi.clearAll();
        await loadData();
      } catch (err) {
        console.error('Failed to clear opportunities:', err);
      }
    }
  };

  const statCards = stats ? [
    {
      label: 'Opportunities Found',
      value: stats.total_opportunities,
      icon: Search,
      gradient: 'linear-gradient(135deg, #4c6ef5, #5c7cfa)',
      glow: 'rgba(76, 110, 245, 0.3)',
    },
    {
      label: 'Matched & Ranked',
      value: stats.matched_opportunities,
      icon: Target,
      gradient: 'linear-gradient(135deg, #7048e8, #845ef7)',
      glow: 'rgba(112, 72, 232, 0.3)',
    },
    {
      label: 'Pending Approvals',
      value: stats.pending_approvals,
      icon: Clock,
      gradient: 'linear-gradient(135deg, #f06595, #e64980)',
      glow: 'rgba(240, 101, 149, 0.3)',
    },
    {
      label: 'Submitted',
      value: stats.submitted_applications,
      icon: Send,
      gradient: 'linear-gradient(135deg, #20c997, #12b886)',
      glow: 'rgba(32, 201, 151, 0.3)',
    },
  ] : [];

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="glass-card p-6">
              <div className="skeleton h-4 w-24 mb-3" />
              <div className="skeleton h-8 w-16" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">
            <span className="gradient-text">Command Center</span>
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            AI-powered opportunity discovery & auto-application
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={clearAll}
            className="btn-danger"
          >
            Clear All
          </button>
          <button
            onClick={runDiscovery}
            disabled={discovering}
            className="btn-primary"
          >
            {discovering ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Radar className="w-4 h-4" />
            )}
            {discovering ? 'Scanning...' : 'Discover'}
          </button>
          <button
            onClick={runMatching}
            disabled={matching}
            className="btn-secondary"
          >
            {matching ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            {matching ? 'Matching...' : 'Match All'}
          </button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map(({ label, value, icon: Icon, gradient, glow }, i) => (
          <div key={i} className="glass-card p-6 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                   style={{ background: gradient, boxShadow: `0 4px 15px ${glow}` }}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <TrendingUp className="w-4 h-4 text-gray-500" />
            </div>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-sm text-gray-400 mt-1">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Opportunities */}
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary-400" />
              Top Opportunities
            </h2>
            <Link to="/opportunities" className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1 transition-colors">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {recentOpps.length === 0 ? (
            <div className="text-center py-12">
              <Radar className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">No opportunities discovered yet</p>
              <p className="text-gray-500 text-sm mt-1">Click "Discover" to scan for opportunities</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentOpps.map((opp, i) => (
                <Link
                  key={opp.id}
                  to={`/opportunities`}
                  className="flex items-center gap-4 p-4 rounded-xl transition-all duration-300 animate-slide-up"
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    animationDelay: `${i * 0.1}s`,
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'}
                >
                  <ScoreRing score={opp.match_score} size={48} />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-white truncate">{opp.name}</h3>
                    <p className="text-xs text-gray-400 mt-0.5 truncate">
                      {opp.organizer || 'Unknown organizer'} • Deadline: {opp.deadline || 'TBD'}
                    </p>
                  </div>
                  <StatusBadge status={opp.status} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions & Upcoming Deadlines */}
        <div className="space-y-6">
          {/* Avg Score */}
          {stats && stats.avg_match_score > 0 && (
            <div className="glass-card p-6 text-center">
              <h3 className="text-sm font-medium text-gray-400 mb-4">Average Match Score</h3>
              <ScoreRing score={Math.round(stats.avg_match_score)} size={80} />
            </div>
          )}

          {/* Upcoming Deadlines */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Upcoming Deadlines
            </h3>
            {stats?.upcoming_deadlines?.length > 0 ? (
              <div className="space-y-3">
                {stats.upcoming_deadlines.map((d, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-gray-300 truncate flex-1 mr-2">{d.name}</span>
                    <span className="text-primary-400 font-mono text-xs whitespace-nowrap">{d.deadline}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No upcoming deadlines</p>
            )}
          </div>

          {/* Quick Links */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Link to="/profile" className="flex items-center gap-3 p-3 rounded-xl text-sm text-gray-300 hover:text-white transition-all"
                    style={{ background: 'rgba(255,255,255,0.02)' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}>
                <Sparkles className="w-4 h-4 text-accent-400" />
                Update Profile
              </Link>
              <Link to="/applications" className="flex items-center gap-3 p-3 rounded-xl text-sm text-gray-300 hover:text-white transition-all"
                    style={{ background: 'rgba(255,255,255,0.02)' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}>
                <FileText className="w-4 h-4 text-primary-400" />
                Review Applications
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function FileText(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
         strokeLinejoin="round" {...props}>
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
      <path d="M14 2v4a2 2 0 0 0 2 2h4" />
      <path d="M10 9H8" /><path d="M16 13H8" /><path d="M16 17H8" />
    </svg>
  );
}
