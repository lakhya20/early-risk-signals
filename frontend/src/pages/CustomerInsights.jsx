import React, { useState } from 'react'
import '../styles/insights.css'
import '../styles/forms.css'
import TrendChart from '../components/TrendChart'
import { getCustomer, getAlerts } from '../services/api'

export default function CustomerInsights() {
  const [id, setId] = useState('')
  const [info, setInfo] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(false)

  const fetch = async () => {
    if (!id.trim()) return

    setLoading(true)
    try {
      const [customerData, alertsData] = await Promise.all([
        getCustomer(id).catch(() => null),
        getAlerts(id).catch(() => [])
      ])
      setInfo(customerData)
      setAlerts(Array.isArray(alertsData) ? alertsData : [])
    } catch (e) {
      console.error(e)
      setInfo(null)
      setAlerts([])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetch()
    }
  }

  return (
    <div className="page insights-page">
      <h1 className="page-title">Customer Insights</h1>
      <p className="page-subtitle">Detailed customer profile and risk analysis</p>

      <div className="insights-top-row">
        <div className="search-container neon-card glow-panel">
          <div className="search-row" style={{ margin: 0 }}>
            <input
              placeholder="Enter Customer ID"
              value={id}
              onChange={(e) => setId(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button className="btn-glow" onClick={fetch} disabled={loading || !id.trim()}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        <div className="quick-summary neon-card glow-panel">
          {info ? (
            <div>
              <div className="summary-title">Quick Summary</div>
              <div style={{ marginTop: '16px' }}>
                <div style={{ fontSize: '14px', color: '#9fcbdc', marginBottom: '8px' }}>Customer ID</div>
                <div style={{ fontSize: '20px', fontWeight: 700, color: '#00eaff' }}>{info.customer_id || id}</div>
              </div>
              {info.risk_level && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ fontSize: '14px', color: '#9fcbdc', marginBottom: '8px' }}>Risk Level</div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#dfefff' }}>{info.risk_level.toUpperCase()}</div>
                </div>
              )}
            </div>
          ) : (
            <div className="placeholder" style={{ padding: '24px' }}>
              Search for a customer to view summary
            </div>
          )}
        </div>
      </div>

      <div className="insights-grid">
        <div className="profile-card neon-card glow-panel">
          {info ? (
            <>
              <div className="profile-header">
                <div>
                  <div className="profile-title">Customer Profile</div>
                  <div className="profile-id">ID: {info.customer_id || id}</div>
                </div>
                <div className="risk-score-display">
                  <div className="risk-score-value">
                    {(info.risk_score || info.score || 0).toFixed(3)}
                  </div>
                  <div className="risk-score-label">Risk Score</div>
                </div>
              </div>
              <div className="profile-details">
                {info.credit_limit && (
                  <div className="detail-group">
                    <div className="detail-label">Credit Limit</div>
                    <div className="detail-value">₹{info.credit_limit.toLocaleString()}</div>
                  </div>
                )}
                {info.utilisation_pct !== undefined && (
                  <div className="detail-group">
                    <div className="detail-label">Utilization</div>
                    <div className="detail-value">{info.utilisation_pct}%</div>
                  </div>
                )}
                {info.risk_level && (
                  <div className="detail-group">
                    <div className="detail-label">Risk Level</div>
                    <div className="detail-value">{info.risk_level.toUpperCase()}</div>
                  </div>
                )}
                {info.model_version && (
                  <div className="detail-group">
                    <div className="detail-label">Model Version</div>
                    <div className="detail-value">{info.model_version}</div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="placeholder">
              <div className="placeholder-icon-large">◐</div>
              Search for a customer to view detailed insights
            </div>
          )}
        </div>

        <div className="alerts-card neon-card glow-panel">
          <div className="alerts-title">Alerts</div>
          {alerts.length === 0 ? (
            <div className="placeholder" style={{ padding: '24px' }}>
              No alerts for this customer
            </div>
          ) : (
            alerts.map((alert, idx) => (
              <div key={idx} className="alert-item">
                <div className="alert-message">{alert.message || alert}</div>
                {alert.created_at && (
                  <div className="alert-date">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {info && (
        <div className="trajectory-chart neon-card glow-panel">
          <div className="trajectory-title">Risk Trajectory</div>
          <TrendChart />
        </div>
      )}
    </div>
  )
}
