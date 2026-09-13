import { useState, useEffect } from 'react';
import {
  FileText,
  Image,
  Check,
  X,
  Eye,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  ClipboardList,
  ShieldCheck,
  AlertTriangle,
} from 'lucide-react';
import { applicationsApi } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import ScoreRing from '../components/ScoreRing';

export default function Applications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const [approving, setApproving] = useState(null);
  const [fieldLogs, setFieldLogs] = useState({});
  const [screenshotModal, setScreenshotModal] = useState(null);

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      const res = await applicationsApi.list();
      setApplications(res.data.applications || []);
    } catch (err) {
      console.error('Failed to load:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id, approved) => {
    setApproving(id);
    try {
      await applicationsApi.approve(id, approved);
      await loadApplications();
    } catch (err) {
      console.error('Approval failed:', err);
    } finally {
      setApproving(null);
    }
  };

  const loadFieldLogs = async (id) => {
    if (fieldLogs[id]) return;
    try {
      const res = await applicationsApi.getFieldLogs(id);
      setFieldLogs(prev => ({ ...prev, [id]: res.data.field_logs || [] }));
    } catch (err) {
      console.error('Failed to load field logs:', err);
    }
  };

  const toggleExpand = async (id) => {
    if (expanded === id) {
      setExpanded(null);
    } else {
      setExpanded(id);
      await loadFieldLogs(id);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">
            <span className="gradient-text">Applications</span>
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            Track auto-filled applications & approve submissions
          </p>
        </div>
        <button onClick={loadApplications} className="btn-secondary">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Safety Notice */}
      <div className="glass-card p-4 mb-6 flex items-center gap-3"
           style={{ borderColor: 'rgba(47, 158, 68, 0.2)' }}>
        <ShieldCheck className="w-5 h-5 text-green-400 flex-shrink-0" />
        <p className="text-sm text-gray-300">
          <strong className="text-green-400">Human-in-the-loop:</strong>{' '}
          All applications require your explicit approval before submission. Review the screenshot and field logs before clicking approve.
        </p>
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="glass-card p-6">
              <div className="skeleton h-6 w-64 mb-2" />
              <div className="skeleton h-4 w-48" />
            </div>
          ))}
        </div>
      ) : applications.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-300 mb-2">No applications yet</h3>
          <p className="text-gray-500 text-sm">
            Auto-fill an application from the Opportunities page to get started
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app, i) => (
            <div key={app.id} className="glass-card-interactive overflow-hidden animate-slide-up"
                 style={{ animationDelay: `${Math.min(i, 10) * 0.05}s` }}>
              {/* Main Row */}
              <div
                className="p-5 flex items-center gap-4"
                onClick={() => toggleExpand(app.id)}
              >
                <ScoreRing score={app.match_score} size={48} />

                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-white truncate">
                    {app.opportunity_name || `Application #${app.id}`}
                  </h3>
                  <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                    {app.filled_at && <span>Filled: {new Date(app.filled_at).toLocaleString()}</span>}
                    {app.submitted_at && <span>Submitted: {new Date(app.submitted_at).toLocaleString()}</span>}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <StatusBadge status={app.status} />

                  {/* Approval Buttons */}
                  {app.status === 'awaiting_approval' && (
                    <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                      <button
                        onClick={() => handleApprove(app.id, true)}
                        disabled={approving === app.id}
                        className="btn-success text-xs px-3 py-1.5"
                      >
                        {approving === app.id ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                        Approve & Submit
                      </button>
                      <button
                        onClick={() => handleApprove(app.id, false)}
                        disabled={approving === app.id}
                        className="btn-danger text-xs px-3 py-1.5"
                      >
                        <X className="w-3 h-3" /> Reject
                      </button>
                    </div>
                  )}

                  {expanded === app.id
                    ? <ChevronUp className="w-4 h-4 text-gray-500" />
                    : <ChevronDown className="w-4 h-4 text-gray-500" />
                  }
                </div>
              </div>

              {/* Expanded Detail */}
              {expanded === app.id && (
                <div className="px-5 pb-5 pt-2 border-t animate-fade-in"
                     style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Screenshot */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3 flex items-center gap-1.5">
                        <Image className="w-3.5 h-3.5" /> Form Screenshot
                      </h4>
                      {app.screenshot_path ? (
                        <div className="space-y-3">
                          <div className="flex gap-2">
                            <a
                              href={applicationsApi.getScreenshot(app.id)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn-secondary text-xs px-3 py-1.5 flex-1 justify-center"
                            >
                              Open in New Tab
                            </a>
                            <a
                              href={applicationsApi.getScreenshot(app.id)}
                              download={`screenshot-app-${app.id}.png`}
                              className="btn-primary text-xs px-3 py-1.5 flex-1 justify-center"
                            >
                              Download
                            </a>
                          </div>
                          <div className="relative group cursor-pointer" onClick={() => setScreenshotModal(app.id)}>
                            <img
                              src={applicationsApi.getScreenshot(app.id)}
                              alt="Filled form screenshot"
                              className="w-full rounded-xl border transition-all duration-300 group-hover:border-primary-500/30"
                              style={{ borderColor: 'rgba(255,255,255,0.06)' }}
                            />
                            <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl">
                              <Eye className="w-8 h-8 text-white" />
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="p-8 rounded-xl text-center text-sm text-gray-500"
                             style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
                          No screenshot available
                        </div>
                      )}
                    </div>

                    {/* Field Logs */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3 flex items-center gap-1.5">
                        <ClipboardList className="w-3.5 h-3.5" /> Field Fill Log
                      </h4>
                      {fieldLogs[app.id] && fieldLogs[app.id].length > 0 ? (
                        <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
                          {fieldLogs[app.id].map((log, j) => (
                            <div key={j} className="p-3 rounded-lg text-xs"
                                 style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                              <div className="flex items-center justify-between mb-1.5">
                                <span className="font-semibold text-primary-300">{log.field_label}</span>
                                <span className="text-gray-500 font-mono">{log.field_type}</span>
                              </div>
                              <p className="text-gray-300 mb-1 break-all">
                                <span className="text-gray-500">Value:</span> {log.filled_value || '(empty)'}
                              </p>
                              <p className="text-gray-500 italic">
                                {log.reasoning}
                              </p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">No field logs available</p>
                      )}

                      {app.error_message && (
                        <div className="mt-4 p-3 rounded-lg flex items-start gap-2"
                             style={{ background: 'rgba(224, 49, 49, 0.1)', border: '1px solid rgba(224, 49, 49, 0.2)' }}>
                          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-red-300">{app.error_message}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Screenshot Modal */}
      {screenshotModal && (
        <div
          className="fixed inset-0 z-50 flex flex-col items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
          onClick={() => setScreenshotModal(null)}
        >
          <div className="flex gap-4 mb-4" onClick={e => e.stopPropagation()}>
            <a 
              href={applicationsApi.getScreenshot(screenshotModal)} 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-secondary bg-white/10 hover:bg-white/20 text-white border-0"
            >
              Open in New Tab
            </a>
            <a 
              href={applicationsApi.getScreenshot(screenshotModal)} 
              download={`screenshot-app-${screenshotModal}.png`}
              className="btn-primary"
            >
              Download
            </a>
          </div>
          <div className="max-w-4xl max-h-[80vh] overflow-auto rounded-2xl" onClick={e => e.stopPropagation()}>
            <img
              src={applicationsApi.getScreenshot(screenshotModal)}
              alt="Full form screenshot"
              className="w-full rounded-2xl"
            />
          </div>
          <button
            className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
            onClick={() => setScreenshotModal(null)}
          >
            <X className="w-6 h-6 text-white" />
          </button>
        </div>
      )}
    </div>
  );
}
