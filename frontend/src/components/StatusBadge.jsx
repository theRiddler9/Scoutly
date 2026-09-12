export default function StatusBadge({ status }) {
  const statusMap = {
    found: { label: 'Found', className: 'badge-found' },
    matched: { label: 'Matched', className: 'badge-matched' },
    pending: { label: 'Pending', className: 'badge-found' },
    filling: { label: 'Filling...', className: 'badge-filling' },
    filled: { label: 'Filled', className: 'badge-matched' },
    awaiting_approval: { label: 'Awaiting Approval', className: 'badge-awaiting' },
    approved: { label: 'Approved', className: 'badge-submitted' },
    submitted: { label: 'Submitted', className: 'badge-submitted' },
    failed: { label: 'Failed', className: 'badge-failed' },
    rejected: { label: 'Rejected', className: 'badge-failed' },
    archived: { label: 'Archived', className: 'badge-found' },
  };

  const info = statusMap[status] || { label: status, className: 'badge-found' };

  return (
    <span className={info.className}>
      <span className="w-1.5 h-1.5 rounded-full inline-block"
            style={{
              background: 'currentColor',
              boxShadow: `0 0 6px currentColor`,
            }} />
      {info.label}
    </span>
  );
}
