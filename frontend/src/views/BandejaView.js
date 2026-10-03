/**
 * Vista de Bandeja Priorizada de Casos Derivados (F1).
 * Referencia Cruzada:
 * - HU E2: HU-UI-01 (Vista de Bandeja Priorizada por SLA y Filtros de Causal)
 * - HU E1: HU-15 (Listado de casos derivados y priorización) / DEC-05 / FR-F1-01
 */

import { fetchCasos, fetchMetricas } from '../api.js';

export function renderBandejaView(container, onSelectCaso) {
  container.innerHTML = `
    <!-- Barra Superior de KPIs Operacionales -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Casos en Cola F1</span>
          <div class="text-2xl font-black text-slate-800" id="kpi-pendientes">-</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-lg">
          📋
        </div>
      </div>

      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">SLA Crítico (&lt;1h)</span>
          <div class="text-2xl font-black text-rose-600 flex items-center space-x-1" id="kpi-criticos">
            <span>-</span>
          </div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-lg animate-pulse">
          ⏱️
        </div>
      </div>

      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Alertas de Fraude</span>
          <div class="text-2xl font-black text-amber-600" id="kpi-fraude">-</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-lg">
          🛡️
        </div>
      </div>

      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Validaciones Facturadas</span>
          <div class="text-2xl font-black text-emerald-600" id="kpi-facturadas">-</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">
          ✅
        </div>
      </div>
    </div>

    <!-- Barra de Herramientas, Búsqueda y Filtros -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-col md:flex-row gap-3 items-center justify-between">
      <div class="w-full md:w-80 relative">
        <input
          type="text"
          id="search-input"
          placeholder="Buscar por ID, RUT o Nombre..."
          class="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
        />
        <span class="absolute left-3 top-2.5 text-slate-400 text-xs">🔍</span>
      </div>

      <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
        <select id="filter-causal" class="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
          <option value="">Todas las Causales</option>
          <option value="ALERTA_CRITICA_FRAUDE">Alerta de Fraude (RF-12)</option>
          <option value="MINIMO_SENAL_INSATISFECHO">Mínimo Violado (RF-11)</option>
          <option value="BAJO_PUNTAJE">Bajo Puntaje &lt;60 (DEC-07)</option>
          <option value="ZONA_GRIS">Zona Gris (60-89)</option>
          <option value="INFORMACION_INCOMPLETA">Info Incompleta (RF-13)</option>
        </select>

        <select id="filter-sla" class="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
          <option value="">Todo el SLA</option>
          <option value="rojo">Crítico (&lt; 1h)</option>
          <option value="amarillo">Urgente (1h - 4h)</option>
          <option value="verde">Normal (&gt; 4h)</option>
        </select>

        <button id="btn-refresh" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg font-medium transition flex items-center space-x-1">
          <span>🔄</span>
          <span>Actualizar</span>
        </button>
      </div>
    </div>

    <!-- Botonera de Acceso Rápido a Casos Canónicos (Criterio C4 / Demostración Rápida) -->
    <div class="bg-indigo-50/70 border border-indigo-100 rounded-xl p-3 mb-6 flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center space-x-2">
        <span class="text-xs font-bold text-indigo-900 uppercase tracking-wide">Demostración Rápida (8 Casos Canónicos):</span>
      </div>
      <div class="flex flex-wrap gap-1.5" id="canonical-buttons">
        <button data-id="CASO-2026-005" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-rose-300 text-rose-700 hover:bg-rose-50 shadow-sm transition" title="Caso con sospecha de fraude activa (RF-12)">
          🛡️ CP-05: Fraude
        </button>
        <button data-id="CASO-2026-008" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-rose-300 text-rose-700 hover:bg-rose-50 shadow-sm transition" title="Caso con SLA venciendo en 25 minutos">
          ⏱️ CP-08: SLA Rojo (&lt;1h)
        </button>
        <button data-id="CASO-2026-003" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-amber-300 text-amber-800 hover:bg-amber-50 shadow-sm transition" title="Caso con puntaje bajo (<60) sin rechazo automático (DEC-07)">
          📉 CP-03: Bajo Puntaje (&lt;60)
        </button>
        <button data-id="CASO-2026-004" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-50 shadow-sm transition" title="Caso con mínimo de prestador insatisfecho (RF-11)">
          ⚠️ CP-02: Mínimo Violado
        </button>
        <button data-id="CASO-2026-007" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-purple-200 text-purple-700 hover:bg-purple-50 shadow-sm transition" title="Caso para probar discrepancia operador (RF-19)">
          ⚖️ CP-07: Discrepancia
        </button>
        <button data-id="CASO-2026-006" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-sm transition" title="Caso con módulo analítico caído (RF-13)">
          🔌 CP-06: Módulo Caído
        </button>
        <button data-id="CASO-2026-002" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-sky-200 text-sky-700 hover:bg-sky-50 shadow-sm transition" title="Caso en zona gris (60-89)">
          ⚖️ CP-04: Zona Gris
        </button>
        <button data-id="CASO-2026-001" class="px-2.5 py-1 text-xs font-semibold rounded bg-white border border-emerald-300 text-emerald-700 hover:bg-emerald-50 shadow-sm transition" title="Caso aprobado automáticamente por F4">
          ✨ CP-01: Auto-Aprobado
        </button>
      </div>
    </div>

    <!-- Contenedor de la Lista / Tabla de Casos -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <h2 class="font-display font-bold text-base text-slate-800">
          Expedientes Derivados para Revisión Asistida
        </h2>
        <span class="text-xs text-slate-400 font-medium" id="total-casos-label">Cargando...</span>
      </div>

      <div class="divide-y divide-slate-100" id="casos-list-container">
        <div class="p-8 text-center text-slate-400">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
          Cargando expedientes...
        </div>
      </div>
    </div>
  `;

  // Carga de Datos y Renderizado Dinámico
  let todosLosCasos = [];

  async function cargarDatos() {
    try {
      const [casos, metricas] = await Promise.all([
        fetchCasos(),
        fetchMetricas(),
      ]);

      todosLosCasos = casos;

      // Actualizar KPIs
      const pendientes = casos.filter(c => c.estado_caso === 'DERIVADO_A_REVISION_ASISTIDA').length;
      const criticos = casos.filter(c => c.sla?.estado_sla === 'rojo').length;
      const fraude = casos.filter(c => c.senales_analiticas?.alerta_fraude_activa).length;

      document.getElementById('kpi-pendientes').textContent = pendientes;
      document.getElementById('kpi-criticos').textContent = criticos;
      document.getElementById('kpi-fraude').textContent = fraude;
      document.getElementById('kpi-facturadas').textContent = metricas.total_validaciones_cobrables ?? 0;

      filtrarYRenderizar();
    } catch (err) {
      document.getElementById('casos-list-container').innerHTML = `
        <div class="p-8 text-center text-rose-600">
          <p class="font-bold">Error al cargar expedientes</p>
          <p class="text-xs text-slate-500 mt-1">${err.message}</p>
        </div>
      `;
    }
  }

  function filtrarYRenderizar() {
    const texto = document.getElementById('search-input').value.toLowerCase().trim();
    const causal = document.getElementById('filter-causal').value;
    const slaFiltro = document.getElementById('filter-sla').value;

    const filtrados = todosLosCasos.filter(caso => {
      // Filtro texto
      const matchTexto = !texto || (
        caso.caso_id.toLowerCase().includes(texto) ||
        caso.asegurado.nombre.toLowerCase().includes(texto) ||
        caso.asegurado.rut.toLowerCase().includes(texto) ||
        caso.prestador.nombre.toLowerCase().includes(texto)
      );

      // Filtro causal
      const matchCausal = !causal || (
        caso.resultado_f4?.causal_derivacion === causal ||
        (causal === 'ALERTA_CRITICA_FRAUDE' && caso.senales_analiticas?.alerta_fraude_activa)
      );

      // Filtro SLA
      const matchSla = !slaFiltro || caso.sla?.estado_sla === slaFiltro;

      return matchTexto && matchCausal && matchSla;
    });

    document.getElementById('total-casos-label').textContent = `${filtrados.length} expediente(s) encontrado(s)`;
    renderListaCasos(filtrados);
  }

  function renderListaCasos(casos) {
    const listContainer = document.getElementById('casos-list-container');

    if (casos.length === 0) {
      listContainer.innerHTML = `
        <div class="p-12 text-center text-slate-400">
          <div class="text-3xl mb-2">📭</div>
          <p class="font-medium text-slate-600">No se encontraron expedientes con los filtros seleccionados</p>
          <p class="text-xs text-slate-400 mt-1">Pruebe limpiando los filtros o utilizando los botones de casos canónicos.</p>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = casos.map(caso => {
      // Badge Causal
      let causalBadge = '';
      const causal = caso.resultado_f4?.causal_derivacion;
      const esFraude = caso.senales_analiticas?.alerta_fraude_activa;

      if (esFraude || causal === 'ALERTA_CRITICA_FRAUDE') {
        causalBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-700 border border-rose-300">
          🚨 Alerta Crítica Fraude (RF-12)
        </span>`;
      } else if (causal === 'MINIMO_SENAL_INSATISFECHO') {
        causalBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
          ⚠️ Mínimo Violado (RF-11)
        </span>`;
      } else if (causal === 'BAJO_PUNTAJE') {
        causalBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-100 text-indigo-800 border border-indigo-300">
          📉 Bajo Puntaje &lt;60 (DEC-07)
        </span>`;
      } else if (causal === 'ZONA_GRIS') {
        causalBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sky-100 text-sky-800 border border-sky-300">
          ⚖️ Zona Gris (60-89)
        </span>`;
      } else if (causal === 'INFORMACION_INCOMPLETA') {
        causalBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-200 text-slate-700 border border-slate-300">
          🔌 Info Incompleta (RF-13)
        </span>`;
      } else if (caso.estado_caso === 'APROBADO_AUTOMATICO') {
        causalBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
          ✨ Aprobado Automático (F4)
        </span>`;
      }

      // Badge SLA
      let slaBadge = '';
      const estadoSla = caso.sla?.estado_sla;
      const tiempoMinutos = caso.sla?.tiempo_restante_minutos;
      const horas = Math.floor(Math.abs(tiempoMinutos || 0) / 60);
      const mins = Math.abs(tiempoMinutos || 0) % 60;
      const tiempoTexto = tiempoMinutos >= 0 ? `${horas}h ${mins}m restantes` : `Vencido hace ${horas}h`;

      if (estadoSla === 'rojo' || (tiempoMinutos !== undefined && tiempoMinutos <= 60)) {
        slaBadge = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-black bg-rose-100 text-rose-700 border border-rose-300 sla-rojo-pulse">
          ⏱️ SLA Crítico: ${tiempoTexto}
        </span>`;
      } else if (estadoSla === 'amarillo') {
        slaBadge = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
          ⏱️ SLA: ${tiempoTexto}
        </span>`;
      } else {
        slaBadge = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          ⏱️ SLA: ${tiempoTexto}
        </span>`;
      }

      const montoFormateado = `$${caso.prestacion.monto_reclamado.toLocaleString('es-CL')} CLP`;

      return `
        <div class="p-5 hover:bg-slate-50/80 transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 cursor-pointer btn-revisar-caso" data-id="${caso.caso_id}">
          <div class="flex items-start space-x-4">
            <div class="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center font-display font-black text-slate-700 text-sm shrink-0">
              #${caso.caso_id.replace('CASO-2026-', '')}
            </div>
            <div>
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <span class="font-display font-bold text-slate-900 text-base hover:text-indigo-600 transition">
                  ${caso.caso_id}
                </span>
                ${causalBadge}
              </div>
              <div class="text-xs text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
                <span>👤 <strong>${caso.asegurado.nombre}</strong> (${caso.asegurado.rut})</span>
                <span>🏥 ${caso.prestador.nombre}</span>
                <span>📑 ${caso.prestacion.tipo}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-4 shrink-0 w-full sm:w-auto justify-between sm:justify-end">
            <div class="text-right">
              <div class="font-display font-bold text-slate-900 text-sm">${montoFormateado}</div>
              <div class="mt-0.5">${slaBadge}</div>
            </div>

            <button class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs px-4 py-2.5 rounded-lg shadow-sm hover:shadow transition flex items-center space-x-1 shrink-0">
              <span>Revisar</span>
              <span>→</span>
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Listener para abrir caso
    listContainer.querySelectorAll('.btn-revisar-caso').forEach(item => {
      item.addEventListener('click', (e) => {
        const id = item.getAttribute('data-id');
        onSelectCaso(id);
      });
    });
  }

  // Event Listeners
  document.getElementById('search-input').addEventListener('input', filtrarYRenderizar);
  document.getElementById('filter-causal').addEventListener('change', filtrarYRenderizar);
  document.getElementById('filter-sla').addEventListener('change', filtrarYRenderizar);
  document.getElementById('btn-refresh').addEventListener('click', cargarDatos);

  // Acceso rápido a canónicos
  document.getElementById('canonical-buttons').querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      onSelectCaso(id);
    });
  });

  // Ejecutar carga inicial
  cargarDatos();
}
