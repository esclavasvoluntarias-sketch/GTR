const BASE = '/api'

function authHeaders() {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail || `Error ${res.status}`)
  }
  return res.json()
}

export const api = {
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),

  estadoFlota: (base) => request(`/flota/estado${base ? `?base=${base}` : ''}`),
  sincronizar: () => request('/flota/sincronizar', { method: 'POST' }),

  alertas: (resueltas = false) => request(`/alertas?resueltas=${resueltas}`),
  evaluarAlertas: () => request('/alertas/evaluar', { method: 'POST' }),
  justificarAlerta: (id, justificacion) =>
    request(`/alertas/${id}/justificar`, { method: 'PATCH', body: JSON.stringify({ justificacion }) }),

  kpisResumen: () => request('/kpis/resumen'),
  impactoFaltante: (movilId, horas = 4) =>
    request(`/kpis/impacto-faltante?movil_id=${movilId}&horas=${horas}`),

  cargarNomina: (file) => {
    const fd = new FormData()
    fd.append('archivo', file)
    return fetch(`${BASE}/carga/nomina`, { method: 'POST', body: fd, headers: authHeaders() }).then((r) => r.json())
  },
  cargarPlanificacion: (file) => {
    const fd = new FormData()
    fd.append('archivo', file)
    return fetch(`${BASE}/carga/planificacion`, { method: 'POST', body: fd, headers: authHeaders() }).then((r) => r.json())
  },
}
