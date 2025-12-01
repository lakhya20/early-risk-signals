import React, { useState } from 'react'
import '../styles/forms.css'
import '../styles/charts.css'
import axios from 'axios'
import DonutChart from '../components/DonutChart'

export default function RiskScoring() {
  const [form, setForm] = useState({
    customer_id: '',
    credit_limit: 0,
    utilization: 0,
    avg_payment_ratio: 0,
    min_due_paid_freq: 0,
    merchant_mix_index: 0,
    cash_withdrawal_pct: 0,
    recent_spend_change: 0
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value
    setForm({ ...form, [e.target.name]: value })
  }

  const calculate = async () => {
    setLoading(true)
    try {
      const res = await axios.post('http://127.0.0.1:8000/score/predict', {
        customer_id: form.customer_id,
        credit_limit: form.credit_limit,
        utilization: form.utilization,
        avg_payment_ratio: form.avg_payment_ratio,
        min_due_paid_freq: form.min_due_paid_freq,
        merchant_mix_index: form.merchant_mix_index,
        cash_withdrawal_pct: form.cash_withdrawal_pct,
        recent_spend_change: form.recent_spend_change
      })
      setResult(res.data)
    } catch (e) {
      console.error(e)
      alert('Prediction failed. Check backend server logs.')
    } finally {
      setLoading(false)
    }
  }

  // Calculate risk breakdown for donut chart
  const getRiskBreakdown = () => {
    if (!result || !result.risk_score) return { low: 53, medium: 34, high: 13 }
    const score = result.risk_score
    if (score < 0.3) return { low: 70, medium: 25, high: 5 }
    if (score < 0.6) return { low: 30, medium: 50, high: 20 }
    return { low: 10, medium: 30, high: 60 }
  }

  const breakdown = getRiskBreakdown()

  return (
    <div className="page form-page scoring-page">
      <h1 className="page-title">Risk Scoring</h1>
      <p className="page-subtitle">Evaluate customer credit card delinquency risk</p>
      
      <div className="scoring-layout">
        <div className="form-card neon-card glow-panel">
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#bfefff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="section-icon">◉</span>
            Customer Information
          </h2>
          
          <label>
            Customer ID
            <input 
              name="customer_id" 
              value={form.customer_id} 
              onChange={handleChange}
              placeholder="Enter customer ID"
            />
          </label>
          
          <div className="two">
            <label>
              Credit Limit
              <input 
                type="number" 
                name="credit_limit" 
                value={form.credit_limit} 
                onChange={handleChange}
              />
            </label>
            <label>
              Utilization %
              <input 
                type="number" 
                name="utilization" 
                value={form.utilization} 
                onChange={handleChange}
              />
            </label>
          </div>
          
          <div className="two">
            <label>
              Avg Payment Ratio
              <input 
                type="number" 
                step="0.01"
                name="avg_payment_ratio" 
                value={form.avg_payment_ratio} 
                onChange={handleChange}
              />
            </label>
            <label>
              Min Due Paid Freq
              <input 
                type="number" 
                step="0.01"
                name="min_due_paid_freq" 
                value={form.min_due_paid_freq} 
                onChange={handleChange}
              />
            </label>
          </div>
          
          <div className="two">
            <label>
              Merchant Mix Index
              <input 
                type="number" 
                name="merchant_mix_index" 
                value={form.merchant_mix_index} 
                onChange={handleChange}
              />
            </label>
            <label>
              Cash Withdrawal %
              <input 
                type="number" 
                name="cash_withdrawal_pct" 
                value={form.cash_withdrawal_pct} 
                onChange={handleChange}
              />
            </label>
          </div>
          
          <label>
            Recent Spend Change %
            <input 
              type="number" 
              name="recent_spend_change" 
              value={form.recent_spend_change} 
              onChange={handleChange}
            />
          </label>
          
          <button 
            className="btn-glow" 
            onClick={calculate}
            disabled={loading}
            style={{ width: '100%', marginTop: '20px' }}
          >
            {loading ? 'Calculating...' : 'Calculate Risk Score'}
          </button>
        </div>

        <div className="prediction-panel">
          <div className="result-panel">
            {result ? (
              <>
                <div className="score score-value">{(result.risk_score ?? 0).toFixed(3)}</div>
                <div className="level">{result.risk_level || 'LOW'}</div>
                {result.model_version && (
                  <div style={{ marginTop: '16px', fontSize: '12px', color: '#9fcbdc' }}>
                    Model: {result.model_version}
                  </div>
                )}
              </>
            ) : (
              <div className="placeholder">
                <div className="placeholder-icon-large">◉</div>
                Enter customer information and click calculate to see risk assessment
              </div>
            )}
          </div>

          <div className="risk-breakdown-card">
            <div className="chart-title">
              <span className="chart-icon">⚠</span>
              Risk Breakdown
            </div>
            <DonutChart data={{
              labels: ['Low', 'Medium', 'High'],
              values: [breakdown.low, breakdown.medium, breakdown.high]
            }} />
          </div>
        </div>
      </div>
    </div>
  )
}
