import React, { useState } from 'react'
import { api } from '../services/api.js'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.login(username, password)
      onLogin(data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      <div className="hazard-stripe" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
        <form onSubmit={handleSubmit} className="card" style={{ width: 360, '--card-accent': 'var(--amber)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span className="led" />
            <span className="brand">SOS · Red de Asistencia</span>
          </div>
          <div className="page-eyebrow" style={{ marginBottom: 22 }}>Seguimiento de flota en tiempo real</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.68rem', color: 'var(--text-mute)', marginBottom: 4, letterSpacing: '0.06em' }}>
                USUARIO
              </div>
              <input style={{ width: '100%' }} value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.68rem', color: 'var(--text-mute)', marginBottom: 4, letterSpacing: '0.06em' }}>
                CONTRASEÑA
              </div>
              <input style={{ width: '100%' }} type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>

            {error && (
              <div style={{ color: '#ff8264', fontSize: '0.78rem', fontFamily: 'var(--font-mono)', background: 'rgba(216,64,42,0.12)', padding: '8px 10px', border: '1px solid var(--red)' }}>
                ⚠ {error}
              </div>
            )}

            <button className="btn" type="submit" disabled={loading} style={{ marginTop: 6, width: '100%' }}>
              {loading ? 'VERIFICANDO…' : 'Ingresar al panel'}
            </button>
          </div>

          <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border-soft)', fontFamily: 'var(--font-mono)', fontSize: '0.68rem', color: 'var(--text-mute)', display: 'flex', justifyContent: 'space-between' }}>
            <span>6001 / MECA / 10541 / 13305</span>
            <span style={{ color: 'var(--green)' }}>● EN LÍNEA</span>
          </div>
        </form>
      </div>
    </div>
  )
}
