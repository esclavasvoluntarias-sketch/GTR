import React, { useState, useEffect } from 'react'
import { HashRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Flota from './pages/Flota.jsx'
import Alertas from './pages/Alertas.jsx'
import Carga from './pages/Carga.jsx'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  if (!token) {
    return <Login onLogin={setToken} />
  }

  return (
    <HashRouter>
      <div className="app-shell">
        <div className="hazard-stripe" />
        <div className="topbar">
          <div className="brand-block">
            <span className="led" />
            <div>
              <div className="brand">SOS · Red de Asistencia</div>
              <div className="brand-sub">FLOTA_RT — 6001 / MECA / 10541 / 13305</div>
            </div>
          </div>
          <button className="btn-outline" onClick={() => setToken(null)}>Salir</button>
        </div>
        <nav className="nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>Dashboard</NavLink>
          <NavLink to="/flota" className={({ isActive }) => (isActive ? 'active' : '')}>Flota en vivo</NavLink>
          <NavLink to="/alertas" className={({ isActive }) => (isActive ? 'active' : '')}>Alertas</NavLink>
          <NavLink to="/carga" className={({ isActive }) => (isActive ? 'active' : '')}>Carga masiva</NavLink>
        </nav>
        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/flota" element={<Flota />} />
            <Route path="/alertas" element={<Alertas />} />
            <Route path="/carga" element={<Carga />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </HashRouter>
  )
}
