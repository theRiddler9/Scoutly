import { useState, useEffect } from 'react';
import {
  Search,
  Calendar,
  ExternalLink,
  Trophy,
  ChevronDown,
  ChevronUp,
  Sparkles,
  RefreshCw,
  Filter,
  ArrowUpDown,
  Wand2,
} from 'lucide-react';
import { opportunitiesApi, applicationsApi } from '../services/api';
import ScoreRing from '../components/ScoreRing';
import StatusBadge from '../components/StatusBadge';

export default function Opportunities() {
  const [opportunities, setOpportunities] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('score');
  const [expanded, setExpanded] = useState(null);
  const [filling, setFilling] = useState(null);
  const [matching, setMatching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadOpportunities();
  }, [sortBy]);

  const loadOpportunities = async () => {
    setLoading(true);
    try {
      const res = await opportunitiesApi.list({ sort_by: sortBy, limit: 50 });
      setOpportunities(res.data.opportunities || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to load:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMatchAll = async () => {
    setMatching(true);
    try {
      await opportunitiesApi.triggerMatch({ profile_id: 1 });
      await loadOpportunities();
    } catch (err) {
      console.error('Matching failed:', err);
    } finally {
      setMatching(false);
    }
  };

  const handleAutoFill = async (oppId) => {
    setFilling(oppId);
    try {
      await applicationsApi.fill({ opportunity_id: oppId, profile_id: 1 });
      await loadOpportunities();
    } catch (err) {
      console.error('Auto-fill failed:', err);
    } finally {
      setFilling(null);
    }
  };

  const filtered = opportunities.filter(opp =>
    opp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (opp.organizer || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (opp.tags || []).some(t => t.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">
            <span className="gradient-text">Opportunities</span>
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            {total} discovered • Sorted by {sortBy}
          </p>
        </div>
        <button
          onClick={handleMatchAll}
          disabled={matching}
          className="btn-primary"
        >
          {matching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          {matching ? 'Matching...' : 'Match All'}
        </button>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            className="input-field pl-10"
            placeholder="Search opportunities..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          {['score', 'deadline', 'discovered_at', 'name'].map(sort => (
            <button
              key={sort}
              onClick={() => setSortBy(sort)}
              className={`px-3 py-2 rounded-xl text-xs font-medium transition-all duration-300 ${
                sortBy === sort
                  ? 'text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              style={sortBy === sort ? {
                background: 'rgba(76, 110, 245, 0.15)',
                border: '1px solid rgba(76, 110, 245, 0.2)',
              } : {
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
              }}
            >
              {sort === 'discovered_at' ? 'Recent' : sort.charAt(0).toUpperCase() + sort.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="glass-card p-6">
              <div className="flex items-center gap-4">
                <div className="skeleton w-14 h-14 rounded-full" />
                <div className="flex-1">
                  <div className="skeleton h-5 w-48 mb-2" />
                  <div className="skeleton h-4 w-32" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-300 mb-2">No opportunities found</h3>
          <p className="text-gray-500 text-sm">
            {searchQuery ? 'Try a different search query' : 'Run a discovery scan to find opportunities'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((opp, i) => (
            <div
              key={opp.id}
              className="glass-card overflow-hidden animate-slide-up"
              style={{ animationDelay: `${Math.min(i, 10) * 0.05}s` }}
            >
              {/* Main Row */}
              <div
                className="p-5 flex items-center gap-4 cursor-pointer transition-all duration-200"
                onClick={() => setExpanded(expanded === opp.id ? null : opp.id)}
                style={{ background: expanded === opp.id ? 'rgba(255,255,255,0.02)' : 'transparent' }}
              >
                <ScoreRing score={opp.match_score} size={56} />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold text-white truncate">{opp.name}</h3>
                    {opp.qualifies && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded-full font-semibold"
                            style={{ background: 'rgba(47,158,68,0.15)', color: '#69db7c', border: '1px solid rgba(47,158,68,0.2)' }}>
                        Qualified
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    <span>{opp.organizer || 'Unknown'}</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {opp.deadline || 'TBD'}
                    </span>
                    {opp.prize_info && opp.prize_info !== 'Not specified' && (
                      <span className="flex items-center gap-1">
                        <Trophy className="w-3 h-3" />
                        {opp.prize_info.length > 30 ? opp.prize_info.slice(0, 30) + '...' : opp.prize_info}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <StatusBadge status={opp.status} />
                  {expanded === opp.id
                    ? <ChevronUp className="w-4 h-4 text-gray-500" />
                    : <ChevronDown className="w-4 h-4 text-gray-500" />
                  }
                </div>
              </div>

              {/* Expanded Detail */}
              {expanded === opp.id && (
                <div className="px-5 pb-5 pt-2 border-t animate-fade-in"
                     style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      {opp.description && (
                        <div className="mb-4">
                          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Description</h4>
                          <p className="text-sm text-gray-300 leading-relaxed">{opp.description}</p>
                        </div>
                      )}
                      {opp.eligibility_summary && (
                        <div className="mb-4">
                          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Eligibility</h4>
                          <p className="text-sm text-gray-300">{opp.eligibility_summary}</p>
                        </div>
                      )}
                      {opp.tags && opp.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5">
                          {opp.tags.map((tag, j) => (
                            <span key={j} className="px-2 py-0.5 rounded-md text-[10px] font-medium"
                                  style={{ background: 'rgba(76,110,245,0.1)', color: '#91a7ff', border: '1px solid rgba(76,110,245,0.15)' }}>
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div>
                      {opp.match_reasoning && (
                        <div className="mb-4">
                          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">AI Match Analysis</h4>
                          <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">{opp.match_reasoning}</p>
                        </div>
                      )}
                      <div className="flex gap-2 mt-4">
                        {opp.apply_url && (
                          <a
                            href={opp.apply_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-secondary text-sm"
                            onClick={e => e.stopPropagation()}
                          >
                            <ExternalLink className="w-3.5 h-3.5" /> View
                          </a>
                        )}
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAutoFill(opp.id); }}
                          disabled={filling === opp.id}
                          className="btn-primary text-sm"
                        >
                          {filling === opp.id ? (
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Wand2 className="w-3.5 h-3.5" />
                          )}
                          {filling === opp.id ? 'Filling...' : 'Auto-Fill'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
