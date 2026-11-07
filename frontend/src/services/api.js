const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status }
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, options)
  if (response.status === 204) return null
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new ApiError(body.detail || 'The request could not be completed.', response.status)
  return body
}

export const api = {
  extract: (form) => request('/rca/extract', { method: 'POST', body: form }),
  analyze: (payload) => request('/rca/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  fiveWhys: (payload) => request('/rca/five-whys', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  fishbone: (payload) => request('/rca/fishbone', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  rootCauses: (payload) => request('/rca/root-causes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  evidence: (payload) => request('/rca/missing-evidence', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  capa: (payload) => request('/rca/capa', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  create: (payload) => request('/investigations', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  update: (id, payload) => request(`/investigations/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  list: () => request('/investigations'),
  get: (id) => request(`/investigations/${id}`),
  review: (id, payload, role = 'investigator') => request(`/investigations/${id}/review`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Role': role }, body: JSON.stringify(payload) }),
}
