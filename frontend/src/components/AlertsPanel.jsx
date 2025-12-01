const AlertsPanel = ({ alerts = [] }) => {
  if (alerts.length === 0) {
    return (
      <div className="glass-card">
        <div className="section-title">Alerts</div>
        <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-secondary)' }}>
          No alerts
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card">
      <div className="section-title">Alerts</div>
      <div style={{ marginTop: '16px' }}>
        {alerts.map((alert, idx) => (
          <div
            key={idx}
            style={{
              padding: '12px 16px',
              marginBottom: '12px',
              background: 'rgba(236, 72, 153, 0.1)',
              border: '1px solid rgba(236, 72, 153, 0.3)',
              borderRadius: 'var(--radius-md)',
              fontSize: '14px',
              color: 'var(--text-primary)',
            }}
          >
            {alert.message || alert}
          </div>
        ))}
      </div>
    </div>
  )
}

export default AlertsPanel

