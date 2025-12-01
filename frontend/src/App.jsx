import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import RiskScoring from './pages/RiskScoring'
import ModelTraining from './pages/ModelTraining'
import ModelRollback from './pages/ModelRollback'
import CustomerInsights from './pages/CustomerInsights'
import Sidebar from './components/Sidebar'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-root">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/risk" element={<RiskScoring />} />
            <Route path="/train" element={<ModelTraining />} />
            <Route path="/rollback" element={<ModelRollback />} />
            <Route path="/insights" element={<CustomerInsights />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
