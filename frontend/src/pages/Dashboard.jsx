import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Star,
  Clock,
  Send,
  Sparkles,
  Filter,
  MoreVertical,
  Check
} from 'lucide-react';
import { dashboardApi, opportunitiesApi, applicationsApi } from '../services/api';
import ScoreRing from '../components/ScoreRing';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentOpps, setRecentOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fillingId, setFillingId] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, oppsRes] = await Promise.all([
        dashboardApi.getStats(),
        opportunitiesApi.list({ sort_by: 'score', limit: 10 }),
      ]);
      setStats(statsRes.data);
      setRecentOpps(oppsRes.data.opportunities || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoFill = async (e, oppId) => {
    e.preventDefault();
    setFillingId(oppId);
    try {
      await applicationsApi.fill({ opportunity_id: oppId, profile_id: 1 });
      await loadData(); // Refresh to get updated status
    } catch (err) {
      console.error('Auto-fill failed:', err);
    } finally {
      setFillingId(null);
    }
  };

  // Mock static data for the specific badges requested in Figma
  const statCards = [
    {
      label: 'Opportunities Found',
      value: stats?.total_opportunities || 0,
      icon: Search,
      badge: '+34 today',
      badgeColor: 'text-[#20c997]',
      badgeBg: 'bg-[#20c997]/10',
      iconColor: 'text-[#4c6ef5]',
      iconBg: 'bg-[#4c6ef5]/10',
    },
    {
      label: 'Matched & Ranked',
      value: stats?.matched_opportunities || 0,
      icon: Star,
      badge: '+12 today',
      badgeColor: 'text-[#20c997]',
      badgeBg: 'bg-[#20c997]/10',
      iconColor: 'text-[#f06595]',
      iconBg: 'bg-[#f06595]/10',
    },
    {
      label: 'Pending Approvals',
      value: stats?.pending_approvals || 0,
      icon: Clock,
      badge: '2 urgent',
      badgeColor: 'text-[#ffd43b]',
      badgeBg: 'bg-[#ffd43b]/10',
      iconColor: 'text-[#ffd43b]',
      iconBg: 'bg-[#ffd43b]/10',
    },
    {
      label: 'Submitted',
      value: stats?.submitted_applications || 0,
      icon: Send,
      badge: '↑ 8 this week',
      badgeColor: 'text-[#20c997]',
      badgeBg: 'bg-[#20c997]/10',
      iconColor: 'text-[#20c997]',
      iconBg: 'bg-[#20c997]/10',
    },
  ];

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="glass-card p-6 h-32">
              <div className="skeleton h-4 w-24 mb-3" />
              <div className="skeleton h-10 w-16" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card, i) => (
          <div key={i} className="glass-card p-5 relative overflow-hidden group hover:border-[#4c6ef5]/30 transition-colors">
            {/* Top Right Badge */}
            <div className={`absolute top-4 right-4 px-2 py-0.5 rounded-full text-[10px] font-bold ${card.badgeBg} ${card.badgeColor}`}>
              {card.badge}
            </div>
            
            {/* Icon */}
            <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-3 ${card.iconBg}`}>
              <card.icon className={`w-5 h-5 ${card.iconColor}`} />
            </div>
            
            {/* Value & Label */}
            <h2 className="text-3xl font-bold text-white mb-1 tracking-tight">{card.value}</h2>
            <p className="text-sm text-gray-400 font-medium">{card.label}</p>
          </div>
        ))}
      </div>

      {/* Main Table Section */}
      <div className="glass-card overflow-hidden">
        {/* Table Header Area */}
        <div className="p-6 border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white">Live Opportunities</h2>
            <p className="text-sm text-gray-400 mt-1">Ranked by match score • Updated 2 min ago</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 rounded-xl text-sm font-medium text-gray-300 bg-white/5 hover:bg-white/10 hover:text-white transition-colors border border-white/5">
              All categories
            </button>
            <button className="px-4 py-2 rounded-xl text-sm font-medium text-gray-300 bg-white/5 hover:bg-white/10 hover:text-white transition-colors border border-white/5 flex items-center gap-2">
              <Filter className="w-4 h-4" /> Filter
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/5 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <th className="px-6 py-4 font-medium">Score</th>
                <th className="px-6 py-4 font-medium">Opportunity</th>
                <th className="px-6 py-4 font-medium">Deadline</th>
                <th className="px-6 py-4 font-medium">Prize</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {recentOpps.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-400">
                    No opportunities found. Run a discovery scan!
                  </td>
                </tr>
              ) : (
                recentOpps.map((opp) => (
                  <tr key={opp.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <ScoreRing score={opp.match_score} size={44} />
                    </td>
                    <td className="px-6 py-4 min-w-[280px]">
                      <div className="flex flex-col gap-1.5">
                        <Link to={`/opportunities`} className="text-base font-bold text-white hover:text-[#4c6ef5] transition-colors">
                          {opp.name}
                        </Link>
                        <div className="flex flex-wrap gap-1.5">
                          {opp.tags?.slice(0, 3).map((tag, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-white/5 text-gray-400 border border-white/5 uppercase tracking-wider">
                              {tag}
                            </span>
                          ))}
                          {(!opp.tags || opp.tags.length === 0) && (
                            <span className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-white/5 text-gray-400 border border-white/5 uppercase tracking-wider">
                              General
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="text-sm font-semibold text-gray-200">
                          {opp.deadline === 'TBD' ? 'TBD' : opp.deadline}
                        </span>
                        <span className="text-xs text-gray-500 mt-0.5">{opp.organizer || 'Unknown'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-bold text-[#4c6ef5]">
                        {opp.prize_info && opp.prize_info !== 'Not specified' ? opp.prize_info : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={opp.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      {opp.status === 'found' || opp.status === 'matched' ? (
                        <button
                          onClick={(e) => handleAutoFill(e, opp.id)}
                          disabled={fillingId === opp.id}
                          className="px-4 py-2 rounded-xl text-sm font-bold text-white transition-all bg-gradient-to-r from-[#4c6ef5] to-[#7048e8] hover:from-[#5c7cfa] hover:to-[#845ef7] shadow-[0_0_15px_rgba(76,110,245,0.3)] hover:shadow-[0_0_20px_rgba(76,110,245,0.5)] flex items-center gap-2 disabled:opacity-50"
                        >
                          {fillingId === opp.id ? (
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          ) : (
                            <Sparkles className="w-4 h-4" />
                          )}
                          Auto-Fill
                        </button>
                      ) : opp.status === 'awaiting_approval' ? (
                        <button className="px-4 py-2 rounded-xl text-sm font-bold text-[#ffa94d] bg-[#ffa94d]/10 hover:bg-[#ffa94d]/20 transition-colors flex items-center gap-2 border border-[#ffa94d]/20">
                          Review
                        </button>
                      ) : opp.status === 'submitted' || opp.status === 'approved' ? (
                        <button className="px-4 py-2 rounded-xl text-sm font-bold text-[#20c997] bg-[#20c997]/10 flex items-center gap-2 border border-[#20c997]/20" disabled>
                          <Check className="w-4 h-4" /> Done
                        </button>
                      ) : (
                        <button className="p-2 text-gray-500 hover:text-white transition-colors">
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
          <span className="text-gray-500">
            Showing {recentOpps.length} of {stats?.matched_opportunities || 0} matched opportunities
          </span>
          <Link to="/opportunities" className="text-[#4c6ef5] hover:text-[#748ffc] font-medium transition-colors">
            View all opportunities &rarr;
          </Link>
        </div>
      </div>
      
      {/* Bottom spacing */}
      <div className="h-12" />
    </div>
  );
}
