import React, { useEffect, useState, useCallback } from 'react'
import { api } from '../services/api.js'

export default function Flota() {
  const [moviles, setMoviles] = useState([])
  const [base, setBase] = useState('')
  const [loading, setLoading] = useState(true)

  const cargar = useCallback(async () => {
    setLoading(true)
    const data = await api.estadoFlota(base || undefined)
    setMoviles(data)
    setLoading(false)
  }, [base])

  useEffect(() => {
    cargar()
    const interval = setInterval(cargar, 30000)
    return () => clearInterval(interval)
  }, [cargar])

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-eyebrow">Estado GPS</div>
          <h2 className="page-title">Flota en vivo</h2>
        </div>
        <select value={base} onChange={(e) => setBase(e.target.value)}>
          <option value="">Todas las bases</option>
          <option value="6001">6001</option>
          <option value="MECA">MECA</option>
          <option value="10541">10541</option>
          <option value="13305">13305</option>
        </select>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Móvil</th><th>Base</th><th>Servicio</th><th>Agente</th><th>Estado</th><th>Login sistema</th><th>Velocidad</th><th>Última act.</th>
            </tr>
          </thead>
          <tbody>
            {moviles.map((m) => (
              <tr key={m.id}>
                <td style={{ color: 'var(--text)', fontWeight: 600 }}>{m.identificador}</td>
                <td><span className="base-chip">{m.base}</span></td>
                <td>{m.tipo_servicio}</td>
                <td>{m.agente || '-'}</td>
                <td><span className={`dot ${m.encendido ? 'dot-on' : 'dot-off'}`} />{m.encendido ? 'Encendido' : 'Apagado'}</td>
                <td>{m.logueado_sistema ? <span className="badge badge-ok">SI</span> : <span className="badge badge-critica">NO</span>}</td>
                <td>{m.velocidad ? `${m.velocidad.toFixed(0)} km/h` : '-'}</td>
                <td>{m.ultima_actualizacion ? new Date(m.ultima_actualizacion).toLocaleTimeString() : '-'}</td>
              </tr>
            ))}
            {!loading && moviles.length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', color: 'var(--text-dim)' }}>Sin datos. Sincronizá desde el Dashboard.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
