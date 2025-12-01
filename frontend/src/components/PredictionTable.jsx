const PredictionTable = ({ data = [] }) => {
  if (data.length === 0) {
    return (
      <div className="predictions-table">
        <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-secondary)' }}>
          No predictions yet
        </div>
      </div>
    )
  }

  return (
    <div className="predictions-table">
      <table className="table">
        <thead>
          <tr>
            <th>Customer ID</th>
            <th>Risk Score</th>
            <th>Risk Level</th>
            <th>Model Version</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              <td>{row.customer_id || 'N/A'}</td>
              <td>{(row.score || row.risk_score || 0).toFixed(3)}</td>
              <td>
                <span className={`badge badge-${(row.level || row.risk_level || 'low').toLowerCase()}`}>
                  {row.level || row.risk_level || 'Low'}
                </span>
              </td>
              <td>{row.model_version || 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default PredictionTable

