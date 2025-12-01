import React from 'react'
import { NavLink } from 'react-router-dom'
import './Sidebar.css'

export default function Sidebar() {
  return (
    <aside className="sidebar neon-sidebar">
      <div className="brand">
        <div className="logo">N</div>
        <div>
          <div className="brand-text">Risk Signals</div>
          <div className="brand-subtitle">Delinquency Watch</div>
        </div>
      </div>

      <nav className="menu">
        <NavLink to="/dashboard" className={({isActive}) => `menu-item ${isActive ? 'active' : ''}`}>
          <span className="menu-icon">▦</span>
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/risk" className={({isActive}) => `menu-item ${isActive ? 'active' : ''}`}>
          <span className="menu-icon">◉</span>
          <span>Risk Scoring</span>
        </NavLink>
        <NavLink to="/train" className={({isActive}) => `menu-item ${isActive ? 'active' : ''}`}>
          <span className="menu-icon">⚙</span>
          <span>Model Training</span>
        </NavLink>
        <NavLink to="/rollback" className={({isActive}) => `menu-item ${isActive ? 'active' : ''}`}>
          <span className="menu-icon">↶</span>
          <span>Model Rollback</span>
        </NavLink>
        <NavLink to="/insights" className={({isActive}) => `menu-item ${isActive ? 'active' : ''}`}>
          <span className="menu-icon">◐</span>
          <span>Customer Insights</span>
        </NavLink>
      </nav>

      <div className="model-status">
        <div className="model-title">ML System</div>
        <div className="model-version">v2.1.0 Active</div>
      </div>
    </aside>
  )
}
