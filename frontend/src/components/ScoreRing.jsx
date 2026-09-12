export default function ScoreRing({ score, size = 56 }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = ((score || 0) / 100) * circumference;

  const getColor = (s) => {
    if (s >= 80) return '#69db7c';
    if (s >= 60) return '#ffd43b';
    if (s >= 40) return '#ffa94d';
    return '#ff6b6b';
  };

  const color = getColor(score);

  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="4"
        />
        {/* Progress ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          style={{
            transition: 'stroke-dashoffset 1s ease-in-out',
            filter: `drop-shadow(0 0 4px ${color}40)`,
          }}
        />
      </svg>
      <span className="score-value" style={{ color }}>
        {score ?? '—'}
      </span>
    </div>
  );
}
