import React, { useState, useEffect } from 'react'
import '../styles/rollback.css'
import { getModelVersions, rollbackModel } from '../services/api'

export default function ModelRollback() {
  const [versions, setVersions] = useState([])
  const [selectedVersion, setSelectedVersion] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadVersions()
  }, [])

  const loadVersions = async () => {
    try {
      const data = await getModelVersions()
      setVersions(Array.isArray(data) ? data : [])
      setError(null)
    } catch (e) {
      console.error('Failed to load versions:', e)
      setError('Failed to load model versions.')
    }
  }

  const handleRollback = async () => {
    if (!selectedVersion) {
      setMessage('Please select a version first')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const versionId = selectedVersion.version || selectedVersion
      await rollbackModel(versionId)
      setMessage(`Successfully rolled back to version: ${versionId}`)
      await loadVersions()
    } catch (e) {
      setMessage('Failed to rollback model. Check backend logs.')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page rollback-page">
      <h1 className="page-title">Model Rollback</h1>
      <p className="page-subtitle">Revert to a previous model version</p>

      <div className="warning">
        <span className="warning-icon">⚠</span>
        <span>Warning: Rolling back to a previous model version will immediately affect all predictions. Make sure you understand the implications before proceeding.</span>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">✕</span>
          <span>{error}</span>
        </div>
      )}

      <div className="rollback-grid">
        <div className="version-section neon-card glow-panel">
          <div className="section-title">Available Versions</div>
          {versions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">↶</div>
              <div>No model versions available</div>
            </div>
          ) : (
            <div className="versions-list">
              {versions.map((version, idx) => {
                const versionId = version.version || version
                const isSelected = selectedVersion?.version === versionId || selectedVersion === versionId
                return (
                  <div
                    key={idx}
                    className={`version-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => setSelectedVersion(version)}
                  >
                    <div className="version-id">{versionId}</div>
                    <div className="version-meta">
                      <span>AUC: {version.auc?.toFixed(3) || 'N/A'}</span>
                      <span>Accuracy: {version.accuracy ? `${(version.accuracy * 100).toFixed(1)}%` : 'N/A'}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="selected-version-details neon-card glow-panel">
          <div className="section-title">Selected Version</div>
          {selectedVersion ? (
            <>
              <div className="detail-item">
                <div className="detail-label">Version</div>
                <div className="detail-value">{selectedVersion.version || selectedVersion}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">AUC</div>
                <div className="detail-value">{selectedVersion.auc?.toFixed(3) || 'N/A'}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">Accuracy</div>
                <div className="detail-value">
                  {selectedVersion.accuracy ? `${(selectedVersion.accuracy * 100).toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <div className="detail-item">
                <div className="detail-label">Precision</div>
                <div className="detail-value">{selectedVersion.precision?.toFixed(3) || 'N/A'}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">Recall</div>
                <div className="detail-value">{selectedVersion.recall?.toFixed(3) || 'N/A'}</div>
              </div>
              {message && (
                <div className={`message ${message.includes('Successfully') ? 'success' : 'error'}`} style={{ marginTop: '16px' }}>
                  {message}
                </div>
              )}
              <button
                className="btn-glow"
                onClick={handleRollback}
                disabled={loading}
                style={{ width: '100%', marginTop: '24px' }}
              >
                {loading ? 'Rolling back...' : 'Restore Model'}
              </button>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">↶</div>
              <div>Select a version from the list to view details</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
