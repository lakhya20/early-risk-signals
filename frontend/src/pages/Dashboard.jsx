import React, { useState, useEffect } from 'react'
import '../styles/dashboard.css'
import '../styles/cards.css'
import '../styles/charts.css'
import TrendChart from '../components/TrendChart'
import DonutChart from '../components/DonutChart'
import { getTrainingHistory } from '../services/api'

export default function Dashboard() {
  const [activeModel, setActiveModel] = useState(null)

  useEffect(() => {
    const loadModel = async () => {
      try {
        const history = await getTrainingHistory()
        if (history && history.length > 0) {
          setActiveModel(history[0])
        }
      } catch (error) {
        console.error('Failed to load model:', error)
      }
    }
    loadModel()
  }, [])

  return (
    <div className="page dashboard-page">
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">Real-time credit card delinquency monitoring</p>

      <div className="stat-cards">
        <div className="stat-card neon-card glow-panel">
          <div className="stat-icon">◐</div>
          <div className="stat-title">Total Customers</div>
          <div className="stat-value">10,000</div>
          <div className="stat-change positive">+12%</div>
        </div>
        <div className="stat-card neon-card glow-panel">
          <div className="stat-icon">⚠</div>
          <div className="stat-title">High Risk</div>
          <div className="stat-value">1,280</div>
          <div className="stat-change negative">-3%</div>
        </div>
        <div className="stat-card neon-card glow-panel">
          <div className="stat-icon">◉</div>
          <div className="stat-title">Model Accuracy</div>
          <div className="stat-value">94.5%</div>
          <div className="stat-change positive">+2.3%</div>
        </div>
        <div className="stat-card neon-card glow-panel">
          <div className="stat-icon">▦</div>
          <div className="stat-title">Predictions Today</div>
          <div className="stat-value">847</div>
          <div className="stat-change positive">+18%</div>
        </div>
      </div>

      <div className="charts-row">
        <div className="chart-container neon-card glow-panel gradient-bg">
          <div className="chart-title">
            <span className="chart-icon">▦</span>
            Risk Distribution Trend
          </div>
          <TrendChart />
        </div>

        <div className="chart-container neon-card glow-panel gradient-bg">
          <div className="chart-title">
            <span className="chart-icon">⚠</span>
            Current Risk Breakdown
          </div>
          <DonutChart />
        </div>
      </div>

      <div className="active-model neon-card glow-panel">
        <div className="model-left">
          <div className="model-label">ACTIVE MODEL</div>
          <div className="model-version-text">
            {activeModel?.version || 'v2.1.0'}
          </div>
        </div>
        <div className="model-right">
          <div className="metric">
            AUC <strong>{activeModel?.auc?.toFixed(3) || '0.469'}</strong>
          </div>
          <div className="metric">
            PRECISION <strong>{activeModel?.precision?.toFixed(2) || '0.33'}</strong>
          </div>
          <div className="metric">
            RECALL <strong>{activeModel?.recall?.toFixed(2) || '0.25'}</strong>
          </div>
        </div>
      </div>
    </div>
  )
}
