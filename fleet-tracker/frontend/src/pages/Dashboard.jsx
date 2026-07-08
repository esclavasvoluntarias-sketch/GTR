import React, { useEffect, useState, useCallback } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { api } from '../services/api.js'

export default function Dashboard() {
  const [kpis, setKpis] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastSync, setLastSync] = useState(null)

  const cargar = useCallback(async () => {
    setLoading(true)
    const data = await api.kpisResumen()
    setKpis(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    cargar()
    const interval = setInterval(cargar, 60000) // refresco automático cada 60s
    return () => clearInterval(interval)
  }, [cargar])

  async function sincronizarYEvaluar() {
    setLoading(true)
    await api.sincronizar()
    await api.evaluarAlertas()
    await cargar()
    setLastSync(new Date().toLocaleTimeString())
  }

  const totalProyectados = kpis.reduce((s, k) => s + k.proyectados, 0)
  const totalLogueados = kpis.reduce((s, k) => s + k.logueados, 0)
  const totalCriticas = kpis.reduce((s, k) => s + k.alertas_criticas, 0)
  const cumplimientoGlobal = totalProyectados ? Math.round((totalLogueados / totalProyectados) * 100) : 0

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Panel en vivo</div>
          <h2 className="page-title">Dashboard operativo</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {lastSync && <span style={{ color: 'var(--text-mute)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>ÚLT. SYNC {lastSync}</span>}
          <button className="btn" onClick={sincronizarYEvaluar} disabled={loading}>
            {loading ? 'ACTUALIZANDO…' : '⟳ SINCRONIZAR'}
          </button>
        </div>
      </div>

      <div className="grid-kpi">
        <div className="card" style={{ '--card-accent': 'var(--amber)' }}>
          <h3>Cumplimiento global</h3>
          <div className="kpi-value" style={{ color: cumplimientoGlobal >= 90 ? 'var(--green)' : cumplimientoGlobal >= 70 ? 'var(--amber)' : 'var(--red)' }}>
            {cumplimientoGlobal}%
          </div>
          <div className="kpi-sub">{totalLogueados} / {totalProyectados} MÓVILES LOGUEADOS</div>
        </div>
        <div className="card" style={{ '--card-accent': 'var(--red)' }}>
          <h3>Alertas críticas</h3>
          <div className="kpi-value" style={{ color: 'var(--red)' }}>{totalCriticas}</div>
          <div className="kpi-sub">REQUIEREN LLAMADO INMEDIATO</div>
        </div>
        <div className="card" style={{ '--card-accent': 'var(--orange)' }}>
          <h3>Bases monitoreadas</h3>
          <div className="kpi-value" style={{ color: 'var(--orange)' }}>{kpis.length}</div>
          <div className="kpi-sub">6001 · MECA · 10541 · 13305</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20, '--card-accent': 'var(--amber-dim)' }}>
        <h3>Cumplimiento por base</h3>
        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <BarChart data={kpis}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3a343a" />
              <XAxis dataKey="base" stroke="#6f6960" style={{ fontFamily: 'Share Tech Mono', fontSize: 11 }} />
              <YAxis stroke="#6f6960" domain={[0, 100]} style={{ fontFamily: 'Share Tech Mono', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#211e23', border: '1px solid #3a343a', color: '#efe8db', fontFamily: 'Share Tech Mono', fontSize: 12 }} />
              <Bar dataKey="cumplimiento_pct" radius={[0, 0, 0, 0]}>
                {kpis.map((k, i) => (
                  <Cell key={i} fill={k.cumplimiento_pct >= 90 ? '#5ec98b' : k.cumplimiento_pct >= 70 ? '#ffb000' : '#d8402a'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Base</th><th>Proyectados</th><th>Logueados</th><th>Cumplimiento</th><th>Críticas</th><th>Advertencias</th>
            </tr>
          </thead>
          <tbody>
            {kpis.map((k) => (
              <tr key={k.base}>
                <td>{k.base}</td>
                <td>{k.proyectados}</td>
                <td>{k.logueados}</td>
                <td>{k.cumplimiento_pct}%</td>
                <td>{k.alertas_criticas > 0 ? <span className="badge badge-critica">{k.alertas_criticas}</span> : '-'}</td>
                <td>{k.alertas_advertencia > 0 ? <span className="badge badge-advertencia">{k.alertas_advertencia}</span> : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
