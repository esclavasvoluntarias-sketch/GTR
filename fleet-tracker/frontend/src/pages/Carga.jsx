import React, { useState } from 'react'
import { api } from '../services/api.js'

export default function Carga() {
  const [resultNomina, setResultNomina] = useState(null)
  const [resultPlan, setResultPlan] = useState(null)
  const [loading, setLoading] = useState(false)

  async function subirNomina(e) {
    const file = e.target.files[0]
    if (!file) return
    setLoading(true)
    const res = await api.cargarNomina(file)
    setResultNomina(res)
    setLoading(false)
  }

  async function subirPlanificacion(e) {
    const file = e.target.files[0]
    if (!file) return
    setLoading(true)
    const res = await api.cargarPlanificacion(file)
    setResultPlan(res)
    setLoading(false)
  }

  return (
    <div>
      <div className="page-eyebrow">Ingreso de datos</div>
      <h2 className="page-title" style={{ marginBottom: 20 }}>Carga masiva</h2>

      <div className="card" style={{ marginBottom: 16, '--card-accent': 'var(--amber)' }}>
        <h3>Nómina de móviles y agentes</h3>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
          Columnas: identificador | gps_device_id | base | tipo_servicio | agente_legajo | agente_nombre
        </p>
        <input type="file" accept=".xlsx,.xlsm" onChange={subirNomina} disabled={loading} />
        {resultNomina && (
          <div style={{ marginTop: 10, color: 'var(--green)' }}>
            {resultNomina.filas_procesadas} filas procesadas correctamente.
          </div>
        )}
      </div>

      <div className="card" style={{ '--card-accent': 'var(--orange)' }}>
        <h3>Planificación semanal de turnos</h3>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
          Columnas: identificador | fecha (YYYY-MM-DD) | hora_inicio | hora_fin | tipo_servicio | coeficiente
        </p>
        <input type="file" accept=".xlsx,.xlsm" onChange={subirPlanificacion} disabled={loading} />
        {resultPlan && (
          <div style={{ marginTop: 10 }}>
            <div style={{ color: 'var(--green)' }}>{resultPlan.filas_procesadas} filas procesadas correctamente.</div>
            {resultPlan.errores?.length > 0 && (
              <ul style={{ color: 'var(--amber)' }}>
                {resultPlan.errores.map((err, i) => <li key={i}>{err}</li>)}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
