/**
 * Cliente API REST para la Bandeja de Revisión Asistida (F1).
 * Soporta conexión directa a backend FastAPI y fallback a datos locales.
 */

const API_BASE = '/api/v1';
const DEFAULT_TENANT = 'org_aseguradora_piloto';

export async function fetchCasos(filtros = {}) {
  const params = new URLSearchParams();
  if (filtros.estado) params.append('estado', filtros.estado);
  if (filtros.causal) params.append('causal', filtros.causal);
  params.append('ordenar_por_sla', 'true');

  try {
    const res = await fetch(`${API_BASE}/casos?${params.toString()}`, {
      headers: {
        'X-Tenant-ID': DEFAULT_TENANT,
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API backend no disponible, intentando cargar dataset estático local...', err);
    // Fallback a dataset local si el backend estuviese apagado
    try {
      const resLocal = await fetch('/backend/data/dataset.json');
      if (resLocal.ok) return await resLocal.json();
    } catch (_) {}
    return [];
  }
}

export async function fetchCaso(casoId) {
  try {
    const res = await fetch(`${API_BASE}/casos/${encodeURIComponent(casoId)}`, {
      headers: {
        'X-Tenant-ID': DEFAULT_TENANT,
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`Error al consultar caso ${casoId} en API:`, err);
    throw err;
  }
}

export async function enviarDictamen(casoId, payload) {
  try {
    const res = await fetch(`${API_BASE}/casos/${encodeURIComponent(casoId)}/dictamen`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': DEFAULT_TENANT,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error('Error al emitir dictamen:', err);
    throw err;
  }
}

export async function fetchMetricas() {
  try {
    const res = await fetch(`${API_BASE}/metricas/validaciones`, {
      headers: {
        'X-Tenant-ID': DEFAULT_TENANT,
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      total_validaciones_cobrables: 0,
      automaticas_f4: 0,
      asistidas_f1: 0,
      diferencia_auditoria: 0,
    };
  }
}
