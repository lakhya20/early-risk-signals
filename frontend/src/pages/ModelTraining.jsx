import React, { useState, useEffect } from 'react'
import '../styles/training.css'
import axios from 'axios'
import { getTrainingHistory } from '../services/api'

export default function ModelTraining() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [lastTraining, setLastTraining] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const data = await getTrainingHistory()
      setHistory(Array.isArray(data) ? data : [])
      if (data && data.length > 0) {
        setLastTraining(data[0])
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const onFile = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setMessage('')
    }
  }

  const submit = async () => {
    if (!file) {
      setMessage('Please choose dataset (.xlsx or .csv)')
      setMessageType('error')
      return
    }

    setLoading(true)
    setMessage('Training pipeline started successfully.')
    setMessageType('info')

    const fd = new FormData()
    fd.append('file', file)

    try {
      const res = await axios.post('http://127.0.0.1:8000/train/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setMessage(`Training complete! Version: ${res.data.model_version || 'N/A'}`)
      setMessageType('success')
      setFile(null)
      await loadHistory()
    } catch (e) {
      console.error(e)
      setMessage('Failed to trigger training. Check backend logs.')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page training-page">
      <h1 className="page-title">Model Training</h1>
      <p className="page-subtitle">Upload dataset and train new risk prediction model</p>

      <div className="training-grid">
        <div className="training-card neon-card glow-panel">
          <div 
            className="upload-area"
            onClick={() => document.getElementById('file-input').click()}
          >
            <div className="upload-icon">↑</div>
            <div className="upload-text">Drop your file here</div>
            <div className="upload-hint">or click to browse (.csv, .xlsx)</div>
            <div style={{ fontSize: '12px', color: '#9fcbdc', marginTop: '8px' }}>
              Max file size: 10MB
            </div>
            <input
              id="file-input"
              type="file"
              onChange={onFile}
              accept=".csv,.xlsx"
              style={{ display: 'none' }}
            />
            {file && <div className="filename">Selected: {file.name}</div>}
          </div>

          <button 
            className="btn-glow" 
            onClick={submit}
            disabled={loading || !file}
            style={{ width: '100%' }}
          >
            {loading ? 'Training...' : 'Train Model'}
          </button>

          {message && (
            <div className={`message ${messageType}`}>
              {message}
            </div>
          )}
        </div>

        <div className="training-summary neon-card glow-panel">
          <div className="summary-title">Training Summary</div>
          {lastTraining ? (
            <>
              <div className="summary-metric">
                <span className="summary-label">Version</span>
                <span className="summary-value">{lastTraining.version || 'N/A'}</span>
              </div>
              <div className="summary-metric">
                <span className="summary-label">AUC</span>
                <span className="summary-value">{lastTraining.auc?.toFixed(3) || 'N/A'}</span>
              </div>
              <div className="summary-metric">
                <span className="summary-label">Accuracy</span>
                <span className="summary-value">
                  {lastTraining.accuracy ? `${(lastTraining.accuracy * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="summary-metric">
                <span className="summary-label">Precision</span>
                <span className="summary-value">{lastTraining.precision?.toFixed(3) || 'N/A'}</span>
              </div>
              <div className="summary-metric">
                <span className="summary-label">F1 Score</span>
                <span className="summary-value">{lastTraining.f1?.toFixed(3) || 'N/A'}</span>
              </div>
            </>
          ) : (
            <div className="placeholder" style={{ padding: '24px' }}>
              No training data available
            </div>
          )}
        </div>
      </div>

      <div className="history-section">
        <div className="history-title">Training History</div>
        {history.length === 0 ? (
          <div className="card neon-card glow-panel" style={{ textAlign: 'center', padding: '48px' }}>
            <div className="empty-icon">⚙</div>
            <div className="placeholder">No training history available</div>
          </div>
        ) : (
          <div className="history-list">
            {history.map((item, idx) => (
              <div key={idx} className="history-card neon-card glow-panel">
                <div className="history-header">
                  <div className="history-version">{item.version || 'N/A'}</div>
                  <div className="history-date">
                    {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
                <div className="history-metrics">
                  <div className="history-metric">
                    <div className="history-metric-label">AUC</div>
                    <div className="history-metric-value">{item.auc?.toFixed(3) || 'N/A'}</div>
                  </div>
                  <div className="history-metric">
                    <div className="history-metric-label">Accuracy</div>
                    <div className="history-metric-value">
                      {item.accuracy ? `${(item.accuracy * 100).toFixed(1)}%` : 'N/A'}
                    </div>
                  </div>
                  <div className="history-metric">
                    <div className="history-metric-label">Precision</div>
                    <div className="history-metric-value">{item.precision?.toFixed(3) || 'N/A'}</div>
                  </div>
                  <div className="history-metric">
                    <div className="history-metric-label">F1</div>
                    <div className="history-metric-value">{item.f1?.toFixed(3) || 'N/A'}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
