const HistoryCard = ({ version, auc, accuracy, precision, recall, f1, created_at }) => {
  return (
    <div className="history-card">
      <div className="history-header">
        <div className="history-version">{version}</div>
        <div className="history-date">
          {created_at ? new Date(created_at).toLocaleDateString() : 'N/A'}
        </div>
      </div>
      <div className="history-metrics">
        <div className="history-metric">
          <div className="history-metric-label">AUC</div>
          <div className="history-metric-value">{auc?.toFixed(3) || 'N/A'}</div>
        </div>
        <div className="history-metric">
          <div className="history-metric-label">Accuracy</div>
          <div className="history-metric-value">
            {accuracy ? `${(accuracy * 100).toFixed(1)}%` : 'N/A'}
          </div>
        </div>
        <div className="history-metric">
          <div className="history-metric-label">Precision</div>
          <div className="history-metric-value">{precision?.toFixed(3) || 'N/A'}</div>
        </div>
        <div className="history-metric">
          <div className="history-metric-label">F1</div>
          <div className="history-metric-value">{f1?.toFixed(3) || 'N/A'}</div>
        </div>
      </div>
    </div>
  )
}

export default HistoryCard

