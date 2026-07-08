import React, { useEffect, useState, useCallback } from 'react'
import { api } from '../services/api.js'

const MOTIVOS = ['FCO', 'VAC', 'QRX', 'ENF', 'DOC', 'Otro']

export default function Alertas() {
  const [alertas, setAlertas] = useState([])
  const [loading, setLoading] = useState(true)

  const cargar = useCallback(async () => {
    setLoading(true)
    const data = await api.alertas(false)
    setAlertas(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    cargar()
    const interval = setInterval(cargar, 30000)
    return () => clearInterval(interval)
  }, [cargar])

  async function justificar(id, motivo) {
    if (!motivo) return
    await api.justificarAlerta(id, motivo)
    cargar()
  }

  const ordenadas = [...alertas].sort((a, b) => b.minutos_desvio - a.minutos_desvio)

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Motor de reglas</div>
          <h2 className="page-title">Llamados prioritarios</h2>
        </div>
        <span style={{ color: 'var(--amber)', fontSize: '0.78rem', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
          {alertas.length} PENDIENTES
        </span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Móvil</th><th>Severidad</th><th>Motivo</th><th>Min. desvío</th><th>Justificar</th>
            </tr>
          </thead>
          <tbody>
            {ordenadas.map((a) => (
              <tr key={a.id}>
                <td style={{ color: 'var(--text)', fontWeight: 600 }}>{a.identificador_movil}</td>
                <td>
                  <span className={`badge ${a.severidad === 'critica' ? 'badge-critica' : 'badge-advertencia'}`}>
                    {a.severidad.toUpperCase()}
                  </span>
                </td>
                <td>{a.motivo}</td>
                <td>{Math.round(a.minutos_desvio)} min</td>
                <td>
                  <select defaultValue="" onChange={(e) => justificar(a.id, e.target.value)}>
                    <option value="" disabled>Seleccionar...</option>
                    {MOTIVOS.map((m) => <option key={m} value={m}>{m}</option>)}
                  </select>
                </td>
              </tr>
            ))}
            {!loading && ordenadas.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-dim)' }}>Sin alertas pendientes.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
