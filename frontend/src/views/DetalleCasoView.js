/**
 * Vista de Detalle de Expediente: Embudo de Tres Tercios Funcionales (F1).
 * Implementa la estricta jerarquía ergonómica para mitigar el sesgo de anclaje cognitivo (DEC-03 / RNF-08).
 * Referencia Cruzada:
 * - HU E2: HU-UI-02 (Tercio Superior: Ficha y Visor de Evidencias con Bounding Boxes - SIN PUNTAJE)
 * - HU E2: HU-UI-03 (Tercio Medio: Matriz de Señales Analíticas Explicables y Mínimos RF-11/RF-12)
 * - HU E2: HU-UI-04 (Tercio Inferior: Revelación Diferida del Puntaje y Dictamen Soberano DEC-07)
 * - HU E2: HU-UI-05 (Captura Friccional de Justificación y Marca de Discrepancia RF-19)
 */

import { fetchCaso, enviarDictamen } from '../api.js';

export async function renderDetalleCasoView(container, casoId, onBack) {
  container.innerHTML = `
    <div class="py-20 text-center text-slate-400">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto mb-3"></div>
      <p>Cargando expediente ${casoId}...</p>
    </div>
  `;

  let caso;
  try {
    caso = await fetchCaso(casoId);
  } catch (err) {
    container.innerHTML = `
      <div class="p-8 text-center text-rose-600">
        <p class="font-bold text-lg">Error al cargar el expediente</p>
        <p class="text-xs text-slate-500 mt-1">${err.message}</p>
        <button id="btn-err-back" class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold">
          ← Volver a la Bandeja
        </button>
      </div>
    `;
    document.getElementById('btn-err-back')?.addEventListener('click', onBack);
    return;
  }

  // Máscara de RUT del asegurado para cumplimiento normativo y privacidad
  const rutEnmascarado = caso.asegurado.rut.replace(/^(\d{1,2})\.(\d{3})\.(\d{3})/, '$1.***.***');
  const montoFormateado = `$${caso.prestacion.monto_reclamado.toLocaleString('es-CL')} CLP`;

  // Causal badge
  let causalBadge = '';
  const causal = caso.resultado_f4?.causal_derivacion;
  const esFraude = caso.senales_analiticas?.alerta_fraude_activa;

  if (esFraude || causal === 'ALERTA_CRITICA_FRAUDE') {
    causalBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700 border border-rose-300">
      🚨 Alerta Crítica Fraude (RF-12)
    </span>`;
  } else if (causal === 'MINIMO_SENAL_INSATISFECHO') {
    causalBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
      ⚠️ Mínimo Violado (RF-11)
    </span>`;
  } else if (causal === 'BAJO_PUNTAJE') {
    causalBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-300">
      📉 Bajo Puntaje &lt;60 (DEC-07)
    </span>`;
  } else if (causal === 'ZONA_GRIS') {
    causalBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-sky-100 text-sky-800 border border-sky-300">
      ⚖️ Zona Gris (60-89)
    </span>`;
  } else if (causal === 'INFORMACION_INCOMPLETA') {
    causalBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-200 text-slate-700 border border-slate-300">
      🔌 Info Incompleta (RF-13)
    </span>`;
  } else {
    causalBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
      ✨ Aprobado Automático
    </span>`;
  }

  // SLA badge
  const estadoSla = caso.sla?.estado_sla;
  const tiempoMinutos = caso.sla?.tiempo_restante_minutos;
  const horas = Math.floor(Math.abs(tiempoMinutos || 0) / 60);
  const mins = Math.abs(tiempoMinutos || 0) % 60;
  const tiempoTexto = tiempoMinutos >= 0 ? `${horas}h ${mins}m restantes` : `Vencido hace ${horas}h`;

  let slaBadge = '';
  if (estadoSla === 'rojo' || (tiempoMinutos !== undefined && tiempoMinutos <= 60)) {
    slaBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-black bg-rose-100 text-rose-700 border border-rose-300 sla-rojo-pulse">
      ⏱️ SLA Crítico: ${tiempoTexto}
    </span>`;
  } else {
    slaBadge = `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
      ⏱️ SLA: ${tiempoTexto}
    </span>`;
  }

  // Render principal
  container.innerHTML = `
    <!-- Cabecera Adherente (Sticky Header) - INVARIANTE: CERO MENCIÓN DE PUNTAJE (RNF-08) -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 sticky top-16 z-30 backdrop-blur-md bg-white/95">
      <div class="flex items-center space-x-3">
        <button id="btn-back-header" class="text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg transition flex items-center space-x-1">
          <span>←</span>
          <span>Bandeja</span>
        </button>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="font-display font-black text-xl text-slate-900">${caso.caso_id}</h1>
            <span class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">Folio Oficial</span>
          </div>
          <p class="text-xs text-slate-500">Expediente de Siniestro para Revisión Asistida</p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        ${causalBadge}
        ${slaBadge}
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- 1. TERCIO SUPERIOR (Viewport Inicial - min-h-[820px]): Inspección Factual -->
    <!-- ========================================================================= -->
    <div class="tier-superior-container mb-12 flex flex-col">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center space-x-2">
          <span class="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">1</span>
          <h2 class="font-display font-bold text-lg text-slate-900">
            Tercio Superior: Inspección Factual y Evidencia Documental
          </h2>
        </div>
        <span class="text-xs bg-emerald-50 text-emerald-700 font-semibold px-2.5 py-1 rounded-full border border-emerald-200">
          ✓ Modo Anti-Anclaje Activo (Puntaje Oculto)
        </span>
      </div>

      <!-- Split View: Ficha (40%) + Visor (60%) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 items-stretch">
        <!-- Columna Izquierda: Ficha de Reclamación (5 cols) -->
        <div class="lg:col-span-5 flex flex-col space-y-4">
          <!-- Tarjeta Asegurado -->
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <div class="flex items-center space-x-2 mb-3 text-indigo-700">
              <span class="text-base">👤</span>
              <h3 class="font-display font-bold text-sm text-slate-800 uppercase tracking-wide">Antecedentes del Afiliado</h3>
            </div>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between border-b border-slate-100 pb-1.5">
                <span class="text-slate-500 font-medium">Nombre Completo:</span>
                <span class="font-bold text-slate-900">${caso.asegurado.nombre}</span>
              </div>
              <div class="flex justify-between border-b border-slate-100 pb-1.5">
                <span class="text-slate-500 font-medium">R.U.T. Asegurado:</span>
                <span class="font-mono font-semibold text-slate-800">${rutEnmascarado}</span>
              </div>
              <div class="flex justify-between border-b border-slate-100 pb-1.5">
                <span class="text-slate-500 font-medium">N° de Póliza:</span>
                <span class="font-mono text-slate-800">${caso.asegurado.poliza_id}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500 font-medium">Plan de Cobertura:</span>
                <span class="font-semibold text-indigo-600">${caso.asegurado.plan}</span>
              </div>
            </div>
          </div>

          <!-- Tarjeta Prestador -->
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <div class="flex items-center space-x-2 mb-3 text-sky-700">
              <span class="text-base">🏥</span>
              <h3 class="font-display font-bold text-sm text-slate-800 uppercase tracking-wide">Prestador de Salud</h3>
            </div>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between border-b border-slate-100 pb-1.5">
                <span class="text-slate-500 font-medium">Razón Social:</span>
                <span class="font-bold text-slate-900">${caso.prestador.nombre}</span>
              </div>
              <div class="flex justify-between border-b border-slate-100 pb-1.5">
                <span class="text-slate-500 font-medium">R.U.T. Institucional:</span>
                <span class="font-mono text-slate-800">${caso.prestador.rut}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500 font-medium">Registro Superintendencia:</span>
                <span class="font-mono text-slate-800 font-semibold">${caso.prestador.registro_superintendencia}</span>
              </div>
            </div>
          </div>

          <!-- Tarjeta Prestación Reclamada -->
          <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-center space-x-2 mb-3 text-emerald-700">
                <span class="text-base">📑</span>
                <h3 class="font-display font-bold text-sm text-slate-800 uppercase tracking-wide">Acto Médico / Reclamo</h3>
              </div>
              <div class="space-y-2 text-xs">
                <div class="flex justify-between border-b border-slate-100 pb-1.5">
                  <span class="text-slate-500 font-medium">Tipo de Atención:</span>
                  <span class="font-semibold text-slate-900 text-right">${caso.prestacion.tipo}</span>
                </div>
                <div class="flex justify-between border-b border-slate-100 pb-1.5">
                  <span class="text-slate-500 font-medium">Fecha Emisión:</span>
                  <span class="font-mono text-slate-800">${caso.prestacion.fecha_emision}</span>
                </div>
              </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-100 flex items-baseline justify-between bg-slate-50 p-3 rounded-lg">
              <span class="text-xs font-bold text-slate-700 uppercase">Monto Solicitado:</span>
              <span class="font-display font-black text-xl text-emerald-600">${montoFormateado}</span>
            </div>
          </div>
        </div>

        <!-- Columna Derecha: Visor de Evidencias con Bounding Boxes (7 cols) -->
        <div class="lg:col-span-7 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-slate-50 border-b border-slate-200 px-4 py-3 flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="text-xs font-bold text-slate-700 uppercase tracking-wide">Visor de Documentos Oficiales</span>
              <span class="text-[11px] px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-mono">
                ${caso.evidencias[0]?.nombre_archivo || 'Documento.pdf'}
              </span>
            </div>
            <!-- Controles de Zoom -->
            <div class="flex items-center space-x-1">
              <button id="btn-zoom-in" class="w-7 h-7 rounded bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 font-bold text-xs shadow-xs" title="Acercar">+</button>
              <button id="btn-zoom-out" class="w-7 h-7 rounded bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 font-bold text-xs shadow-xs" title="Alejar">-</button>
              <button id="btn-zoom-reset" class="px-2 h-7 rounded bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 font-semibold text-xs shadow-xs" title="Restablecer">100%</button>
            </div>
          </div>

          <!-- Lienzo Documental con BoundingBoxOverlay -->
          <div class="relative flex-1 bg-slate-900/5 min-h-[560px] overflow-auto flex items-center justify-center p-4" id="viewer-container">
            <div class="relative inline-block border border-slate-300 rounded-lg shadow-lg bg-white overflow-hidden transition-transform duration-200" id="document-canvas">
              <img
                src="${caso.evidencias[0]?.archivo_url || ''}"
                alt="Documento médico"
                class="max-w-full max-h-[580px] block select-none pointer-events-none"
              />

              <!-- Inyección de Bounding Boxes -->
              ${caso.evidencias[0]?.hallazgos_espaciales?.map(h => `
                <div
                  style="top: ${h.coordenadas.top}%; left: ${h.coordenadas.left}%; width: ${h.coordenadas.width}%; height: ${h.coordenadas.height}%;"
                  class="bounding-box group"
                  data-hallazgo-id="${h.id}"
                >
                  <span class="absolute -top-3 -right-2 bg-rose-600 text-white text-[10px] font-black px-1.5 py-0.2 rounded-full shadow">!</span>
                  
                  <!-- Tooltip flotante hover -->
                  <div class="invisible group-hover:visible absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-72 p-3 bg-slate-900/95 text-white text-xs rounded-xl shadow-2xl z-30 pointer-events-none border border-slate-700">
                    <div class="font-bold text-rose-300 flex items-center space-x-1 mb-1">
                      <span>⚠️</span>
                      <span>${h.tipo} (${h.severidad.toUpperCase()})</span>
                    </div>
                    <p class="text-slate-200 text-[11px] leading-relaxed">${h.descripcion}</p>
                    <div class="mt-2 text-[10px] text-slate-400 font-mono">ID: ${h.id}</div>
                  </div>
                </div>
              `).join('') || ''}
            </div>
          </div>

          <div class="bg-slate-50 border-t border-slate-200 px-4 py-2.5 flex items-center justify-between text-xs text-slate-500">
            <span>💡 Posicione el cursor sobre los recuadros rojos para inspeccionar anomalías</span>
            <span>Hallazgos espaciales: ${caso.evidencias[0]?.hallazgos_espaciales?.length || 0}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Indicador de Desplazamiento Consciente hacia el Tercio Medio -->
    <div class="text-center my-6">
      <a href="#tercio-medio-seccion" class="inline-flex items-center space-x-2 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition py-2 px-4 rounded-full bg-indigo-50 border border-indigo-200">
        <span>↓ Desplazarse al Tercio Medio (Matriz de Señales Analíticas)</span>
      </a>
    </div>

    <!-- ========================================================================= -->
    <!-- 2. TERCIO MEDIO: Desglose de Señales Analíticas Explicables               -->
    <!-- ========================================================================= -->
    <div id="tercio-medio-seccion" class="pt-8 mb-12">
      <div class="flex items-center space-x-2 mb-4">
        <span class="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">2</span>
        <h2 class="font-display font-bold text-lg text-slate-900">
          Tercio Medio: Matriz de Señales Analíticas Explicables
        </h2>
      </div>

      <!-- Banner de Alerta Crítica de Fraude (RF-12) si aplica -->
      ${esFraude ? `
        <div class="bg-rose-50 border-2 border-rose-400 rounded-xl p-4 mb-6 shadow-sm flex items-start space-x-3">
          <div class="text-2xl">🚨</div>
          <div>
            <h4 class="font-display font-bold text-rose-900 text-sm">ALERTA CRÍTICA DE FRAUDE ACTIVA (Mandato RF-12 / H-03)</h4>
            <p class="text-xs text-rose-800 mt-1">
              ${caso.senales_analiticas.detalle_alerta_fraude || 'Se ha detectado una alteración o inconsistencia grave en los antecedentes probatorios.'}
            </p>
            <p class="text-[11px] text-rose-700 font-semibold mt-1">
              ⚖️ Esta señal posee <strong>precedencia de corte absoluto</strong> sobre cualquier puntaje de confianza. Prohíbe la aprobación desatendida.
            </p>
          </div>
        </div>
      ` : ''}

      <!-- Grid de 4 Señales Analíticas -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        ${renderSignalCard(
          'Autenticidad Documental',
          caso.senales_analiticas.autenticidad_documental,
          '35%',
          70.0
        )}
        ${renderSignalCard(
          'Consistencia de Datos',
          caso.senales_analiticas.consistencia_datos,
          '25%',
          null
        )}
        ${renderSignalCard(
          'Habilitación Prestador',
          caso.senales_analiticas.habilitacion_prestador,
          '20%',
          65.0
        )}
        ${renderSignalCard(
          'Consistencia Identidad',
          caso.senales_analiticas.consistencia_identidad,
          '20%',
          75.0
        )}
      </div>
    </div>

    <!-- Indicador de Desplazamiento hacia el Tercio Inferior Resolutivo -->
    <div class="text-center my-6">
      <a href="#panel-puntaje-confianza" class="inline-flex items-center space-x-2 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition py-2 px-4 rounded-full bg-indigo-50 border border-indigo-200">
        <span>↓ Desplazarse al Tercio Inferior (Revelación de Puntaje y Dictamen Soberano)</span>
      </a>
    </div>

    <!-- ========================================================================= -->
    <!-- 3. TERCIO INFERIOR: Revelación Algorítmica Diferida y Dictamen Soberano   -->
    <!-- ========================================================================= -->
    <div id="panel-puntaje-confianza" class="pt-8 mb-16 border-t-2 border-slate-200">
      <div class="flex items-center space-x-2 mb-6">
        <span class="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">3</span>
        <h2 class="font-display font-bold text-lg text-slate-900">
          Tercio Inferior: Revelación de Puntaje Algorítmico y Dictamen Soberano
        </h2>
      </div>

      <!-- Tarjeta de Puntaje Diferido (DEC-03) -->
      <div class="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-6 sm:p-8 shadow-xl mb-8 relative overflow-hidden">
        <div class="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
          <div class="flex items-center space-x-6">
            <!-- Círculo de Puntaje -->
            <div class="w-24 h-24 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex flex-col items-center justify-center shadow-inner">
              <span class="font-display font-black text-3xl text-white">
                ${caso.resultado_f4?.puntaje_calculado !== null ? caso.resultado_f4?.puntaje_calculado : 'N/D'}
              </span>
              <span class="text-[10px] text-slate-300 uppercase tracking-widest font-bold">/ 100 pts</span>
            </div>

            <div>
              <div class="flex items-center space-x-2 mb-1">
                <span class="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
                  Puntaje Global Ponderado F4
                </span>
                <span class="text-xs text-slate-400">Versión: ${caso.resultado_f4?.version_motor || 'v1.0.0-f4'}</span>
              </div>
              <h3 class="font-display font-bold text-xl text-white">
                ${caso.resultado_f4?.decision_algoritmica || 'DERIVADO_A_REVISION_ASISTIDA'}
              </h3>
              <p class="text-xs text-slate-300 max-w-xl mt-1">
                ${caso.resultado_f4?.detalle_causal || 'Expediente remitido a peritaje asistido conforme a los parámetros de riesgo patrimonial.'}
              </p>
            </div>
          </div>

          <!-- Desglose de Ponderaciones -->
          <div class="bg-white/5 border border-white/10 p-4 rounded-xl text-xs space-y-1 w-full md:w-auto">
            <div class="font-bold text-indigo-200 mb-1">Fórmula Ponderada Aplicada:</div>
            <div class="text-[11px] text-slate-300 font-mono">Autenticidad (35%): +${caso.resultado_f4?.desglose_componentes?.autenticidad_documental ?? '-'} pts</div>
            <div class="text-[11px] text-slate-300 font-mono">Consistencia (25%): +${caso.resultado_f4?.desglose_componentes?.consistencia_datos ?? '-'} pts</div>
            <div class="text-[11px] text-slate-300 font-mono">Prestador (20%): +${caso.resultado_f4?.desglose_componentes?.habilitacion_prestador ?? '-'} pts</div>
            <div class="text-[11px] text-slate-300 font-mono">Identidad (20%): +${caso.resultado_f4?.desglose_componentes?.consistencia_identidad ?? '-'} pts</div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-white/10 text-center text-xs text-indigo-200/80">
          ⚖️ <strong>Soberanía del Liquidador (DEC-07):</strong> Este puntaje es exclusivamente un insumo referencial. Su juicio humano profesional es la única autoridad con validez legal vinculante para resolver este siniestro.
        </div>
      </div>

      <!-- ========================================================================= -->
      <!-- Panel Resolutivo y Dictamen Humano (DEC-07 / RF-18 / RF-19)               -->
      <!-- ========================================================================= -->
      <div class="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-md">
        <h3 class="font-display font-bold text-base text-slate-900 mb-1">
          Emisión de Dictamen Vinculante
        </h3>
        <p class="text-xs text-slate-500 mb-6">
          Seleccione la resolución definitiva del siniestro. Si decide revocar la recomendación algorítmica, se estampará una marca formal de discrepancia (RF-19).
        </p>

        <!-- Selector de Acción de Dictamen (Segmented Controls) -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6" id="action-buttons-group">
          <label class="cursor-pointer border-2 border-slate-200 hover:border-emerald-500 rounded-xl p-4 flex flex-col items-center justify-center text-center transition bg-slate-50/50 has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50/60 has-[:checked]:shadow-sm">
            <input type="radio" name="dictamen-action" value="APROBAR" class="sr-only">
            <span class="text-2xl mb-1">✅</span>
            <span class="font-display font-bold text-slate-900 text-sm">Aprobar Siniestro</span>
            <span class="text-[11px] text-slate-500 mt-0.5">Autoriza liquidación y pago</span>
          </label>

          <label class="cursor-pointer border-2 border-slate-200 hover:border-rose-500 rounded-xl p-4 flex flex-col items-center justify-center text-center transition bg-slate-50/50 has-[:checked]:border-rose-600 has-[:checked]:bg-rose-50/60 has-[:checked]:shadow-sm">
            <input type="radio" name="dictamen-action" value="RECHAZAR" class="sr-only">
            <span class="text-2xl mb-1">🛑</span>
            <span class="font-display font-bold text-slate-900 text-sm">Rechazar Siniestro</span>
            <span class="text-[11px] text-slate-500 mt-0.5">Deniega cobertura por causa legal</span>
          </label>

          <label class="cursor-pointer border-2 border-slate-200 hover:border-amber-500 rounded-xl p-4 flex flex-col items-center justify-center text-center transition bg-slate-50/50 has-[:checked]:border-amber-600 has-[:checked]:bg-amber-50/60 has-[:checked]:shadow-sm">
            <input type="radio" name="dictamen-action" value="SOLICITAR_ANTECEDENTES" class="sr-only">
            <span class="text-2xl mb-1">📨</span>
            <span class="font-display font-bold text-slate-900 text-sm">Solicitar Antecedentes</span>
            <span class="text-[11px] text-slate-500 mt-0.5">Pausa SLA y requiere antecedentes</span>
          </label>
        </div>

        <!-- Banner Reactivo de Discrepancia Detectada (RF-19) -->
        <div id="discrepancy-banner" class="hidden bg-amber-50 border-2 border-amber-300 rounded-xl p-4 mb-6 shadow-sm">
          <div class="flex items-start space-x-3">
            <span class="text-2xl">⚖️</span>
            <div>
              <h4 class="font-display font-bold text-amber-900 text-sm">
                DISCREPANCIA DETECTADA CON EL CRITERIO DEL SISTEMA (RF-19)
              </h4>
              <p class="text-xs text-amber-800 mt-1">
                Su decisión de <strong>Aprobar</strong> contradice la alerta algorítmica previa (Bajo Puntaje o Sospecha de Fraude).
                El sistema estampará inmutablemente la marca <code class="bg-amber-200/80 px-1 py-0.5 rounded font-mono font-bold">discrepancia_detectada = true</code>.
              </p>
              <p class="text-[11px] text-amber-900 font-semibold mt-1">
                ⚠️ Para proceder, debe fundamentar obligatoriamente la resolución técnica, médica o legal en el campo inferior.
              </p>
            </div>
          </div>
        </div>

        <!-- Campo de Justificación Obligatoria (RF-19 / DEC-07) -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <label for="justification-input" class="text-xs font-bold text-slate-700 uppercase tracking-wide">
              Fundamentación Técnica / Clínica de la Resolución
            </label>
            <span class="text-xs text-slate-400" id="char-counter">0 / 15 caracteres mínimos</span>
          </div>
          <textarea
            id="justification-input"
            rows="3"
            placeholder="Ingrese el motivo de su dictamen (ej: 'Se verifica boleta original física autorizada por médico auditor de turno...'). Requerido mínimo 15 caracteres."
            class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white resize-none"
          ></textarea>
          <p class="text-[11px] text-slate-400 mt-1" id="validation-hint">
            * Mandatorio para Rechazos, Solicitud de Antecedentes y Casos con Discrepancia.
          </p>
        </div>

        <!-- Botón de Envío -->
        <div class="flex items-center justify-end space-x-3">
          <button id="btn-cancel-dictamen" class="px-5 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition">
            Cancelar
          </button>
          <button
            id="btn-submit-dictamen"
            disabled
            class="px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transition flex items-center space-x-2"
          >
            <span>Emitir Dictamen Vinculante</span>
            <span>→</span>
          </button>
        </div>
      </div>
    </div>
  `;

  // Controladores de Zoom del Visor
  let currentZoom = 1.0;
  const canvas = document.getElementById('document-canvas');
  document.getElementById('btn-zoom-in')?.addEventListener('click', () => {
    currentZoom = Math.min(2.5, currentZoom + 0.2);
    canvas.style.transform = `scale(${currentZoom})`;
  });
  document.getElementById('btn-zoom-out')?.addEventListener('click', () => {
    currentZoom = Math.max(0.6, currentZoom - 0.2);
    canvas.style.transform = `scale(${currentZoom})`;
  });
  document.getElementById('btn-zoom-reset')?.addEventListener('click', () => {
    currentZoom = 1.0;
    canvas.style.transform = 'scale(1)';
  });

  // Botones de retorno
  document.getElementById('btn-back-header')?.addEventListener('click', onBack);
  document.getElementById('btn-cancel-dictamen')?.addEventListener('click', onBack);

  // Lógica Reactiva de Dictamen y Discrepancias (RF-19)
  const radios = container.querySelectorAll('input[name="dictamen-action"]');
  const discrepancyBanner = document.getElementById('discrepancy-banner');
  const justificationInput = document.getElementById('justification-input');
  const charCounter = document.getElementById('char-counter');
  const submitBtn = document.getElementById('btn-submit-dictamen');

  let selectedAction = null;

  function actualizarValidacion() {
    const text = justificationInput.value.trim();
    const len = text.length;
    charCounter.textContent = `${len} / 15 caracteres mínimos`;

    if (len >= 15) {
      charCounter.classList.remove('text-slate-400', 'text-rose-500');
      charCounter.classList.add('text-emerald-600', 'font-semibold');
    } else {
      charCounter.classList.remove('text-emerald-600', 'font-semibold');
      charCounter.classList.add('text-slate-400');
    }

    const esBajoPuntajeOFraude = (
      caso.resultado_f4?.causal_derivacion === 'BAJO_PUNTAJE' ||
      caso.resultado_f4?.causal_derivacion === 'ALERTA_CRITICA_FRAUDE' ||
      caso.senales_analiticas?.alerta_fraude_activa ||
      (caso.resultado_f4?.puntaje_calculado !== null && caso.resultado_f4?.puntaje_calculado < 60.0)
    );

    const hayDiscrepancia = selectedAction === 'APROBAR' && esBajoPuntajeOFraude;

    if (hayDiscrepancia) {
      discrepancyBanner.classList.remove('hidden');
    } else {
      discrepancyBanner.classList.add('hidden');
    }

    // El botón se habilita si hay acción seleccionada y la justificación tiene >=15 chars
    const requiereJustificacion = (
      selectedAction === 'RECHAZAR' ||
      selectedAction === 'SOLICITAR_ANTECEDENTES' ||
      hayDiscrepancia
    );

    if (!selectedAction) {
      submitBtn.disabled = true;
    } else if (requiereJustificacion && len < 15) {
      submitBtn.disabled = true;
    } else {
      submitBtn.disabled = false;
    }
  }

  radios.forEach(r => {
    r.addEventListener('change', (e) => {
      selectedAction = e.target.value;
      actualizarValidacion();
    });
  });

  justificationInput.addEventListener('input', actualizarValidacion);

  // Envío del dictamen
  submitBtn.addEventListener('click', async () => {
    const text = justificationInput.value.trim();
    const roleSelector = document.getElementById('role-selector');
    const operadorId = roleSelector?.value || 'operador_marco';
    const operadorNombre = roleSelector?.options[roleSelector.selectedIndex]?.text || 'Marco Peñailillo';

    submitBtn.disabled = true;
    submitBtn.textContent = 'Procesando y Sellando...';

    try {
      const res = await enviarDictamen(caso.caso_id, {
        decision: selectedAction,
        motivo_justificacion: text,
        operador_id: operadorId,
        operador_nombre: operadorNombre,
      });

      // Mostrar modal de confirmación con sello criptográfico SHA-256
      mostrarModalConfirmacion(res, onBack);
    } catch (err) {
      alert(`Error al registrar dictamen: ${err.message}`);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Emitir Dictamen Vinculante';
    }
  });
}

function renderSignalCard(titulo, detalle, ponderacion, cotaMinima) {
  const valor = detalle?.valor;
  const noDisponible = valor === null || valor === undefined;

  let badgeMinimo = '';
  let colorBarra = 'bg-emerald-500';
  let colorTexto = 'text-emerald-600';

  if (noDisponible) {
    badgeMinimo = `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-700">Módulo No Disponible</span>`;
    colorBarra = 'bg-slate-300';
    colorTexto = 'text-slate-500';
  } else if (cotaMinima !== null) {
    if (valor < cotaMinima) {
      badgeMinimo = `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-700 border border-rose-300">Mín: ${cotaMinima} (NO CUMPLE)</span>`;
      colorBarra = 'bg-rose-500';
      colorTexto = 'text-rose-600';
    } else {
      badgeMinimo = `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">Mín: ${cotaMinima} (CUMPLE)</span>`;
    }
  } else {
    badgeMinimo = `<span class="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">Sin Mínimo Crítico</span>`;
  }

  const porcentajeAncho = noDisponible ? 0 : Math.min(100, Math.max(0, valor));

  return `
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold text-slate-700 uppercase tracking-wide truncate" title="${titulo}">${titulo}</span>
          ${badgeMinimo}
        </div>
        <div class="flex items-baseline space-x-2 my-2">
          <span class="font-display font-black text-2xl ${colorTexto}">
            ${noDisponible ? 'N/D' : valor}
          </span>
          <span class="text-xs text-slate-400">/ 100</span>
          <span class="text-xs text-slate-500 font-medium ml-auto">Peso: ${ponderacion}</span>
        </div>
      </div>

      <div class="mt-2">
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div class="${colorBarra} h-2 rounded-full transition-all duration-300" style="width: ${porcentajeAncho}%"></div>
        </div>
      </div>
    </div>
  `;
}

function mostrarModalConfirmacion(resultado, onFinalizar) {
  const modal = document.getElementById('modal-container');
  modal.classList.remove('hidden');

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-slate-200 relative animate-in fade-in duration-200">
      <div class="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-2xl mb-4 mx-auto shadow-inner">
        ✓
      </div>

      <h3 class="font-display font-black text-xl text-center text-slate-900 mb-2">
        Dictamen Registrado con Éxito
      </h3>
      <p class="text-xs text-center text-slate-500 mb-6">
        La resolución soberana ha sido procesada, notificada y sellada de forma inmutable.
      </p>

      <div class="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs space-y-2 mb-6">
        <div class="flex justify-between border-b border-slate-200/60 pb-1.5">
          <span class="text-slate-500 font-medium">Expediente:</span>
          <span class="font-bold text-slate-900">${resultado.caso_id}</span>
        </div>
        <div class="flex justify-between border-b border-slate-200/60 pb-1.5">
          <span class="text-slate-500 font-medium">Dictamen Emitido:</span>
          <span class="font-bold text-indigo-700">${resultado.decision}</span>
        </div>
        <div class="flex justify-between border-b border-slate-200/60 pb-1.5">
          <span class="text-slate-500 font-medium">Marca Discrepancia:</span>
          <span class="font-bold ${resultado.discrepancia_detectada ? 'text-amber-600' : 'text-slate-700'}">
            ${resultado.discrepancia_detectada ? 'DETECTADA Y SELLADA (RF-19)' : 'Sin Discrepancia'}
          </span>
        </div>
        <div class="pt-1">
          <span class="text-slate-500 font-medium block mb-1">Sello Criptográfico SHA-256 (RNF-04 / DEC-10):</span>
          <div class="bg-slate-900 text-emerald-400 font-mono text-[10px] p-2 rounded break-all shadow-inner select-all">
            ${resultado.hash_auditoria}
          </div>
        </div>
      </div>

      <button id="btn-modal-close" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-md transition">
        Aceptar y Volver a la Bandeja
      </button>
    </div>
  `;

  document.getElementById('btn-modal-close')?.addEventListener('click', () => {
    modal.classList.add('hidden');
    onFinalizar();
  });
}
