const CustomerCard = ({ customer }) => {
  if (!customer) {
    return (
      <div className="glass-card">
        <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-secondary)' }}>
          No customer selected
        </div>
      </div>
    )
  }

  const riskScore = customer.risk_score || customer.score || 0
  const riskLevel = customer.risk_level || customer.level || 'low'
  
  return (
    <div className="glass-card">
      <div className="section-title">Customer Profile</div>
      <div style={{ marginTop: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
          <div>
            <div className="label">Customer ID</div>
            <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>
              {customer.customer_id || 'N/A'}
            </div>
          </div>
          <div>
            <div className="label">Risk Score</div>
            <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--neon-blue)' }}>
              {riskScore.toFixed(3)}
            </div>
          </div>
        </div>
        <div style={{ marginBottom: '16px' }}>
          <div className="label">Risk Level</div>
          <span className={`badge badge-${riskLevel.toLowerCase()}`}>
            {riskLevel.toUpperCase()}
          </span>
        </div>
        {customer.credit_limit && (
          <div style={{ marginBottom: '16px' }}>
            <div className="label">Credit Limit</div>
            <div style={{ fontSize: '16px', color: 'var(--text-primary)' }}>
              ₹{customer.credit_limit.toLocaleString()}
            </div>
          </div>
        )}
        {customer.utilisation_pct !== undefined && (
          <div style={{ marginBottom: '16px' }}>
            <div className="label">Utilization</div>
            <div style={{ fontSize: '16px', color: 'var(--text-primary)' }}>
              {customer.utilisation_pct}%
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CustomerCard
