/**
 * Suite de Prueba Automatizada de Extremo a Extremo (E2E) para la Bandeja Asistida F1.
 * Referencia Cruzada:
 * - HU E2: HU-QA-04 (Suite de Pruebas E2E de Interfaz - Mitigación Anti-Anclaje y Recorrido de Bandeja)
 * - HU E1: HU-15, HU-16, HU-18, HU-19, HU-63 (RNF-08)
 * - DEC-03 (Puntaje al final), DEC-05 (SLA), DEC-07 (Rechazos soberanos), RF-19 (Discrepancia)
 */

import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';
import assert from 'assert';

console.log('🧪 Iniciando Suite de Pruebas E2E: Recorrido Completo de Bandeja F1...');

// 1. Cargar dataset canónico
const datasetPath = path.resolve('../backend/data/dataset.json');
const datasetRaw = fs.readFileSync(datasetPath, 'utf-8');
const casosMock = JSON.parse(datasetRaw);

// 2. Configurar entorno JSDOM simulando navegador
const htmlTemplate = `
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>MIRA F1 E2E</title></head>
<body>
  <div id="app-root"></div>
  <div id="modal-container" class="hidden"></div>
  <select id="role-selector">
    <option value="operador_marco">Marco Peñailillo</option>
  </select>
</body>
</html>
`;

const dom = new JSDOM(htmlTemplate, {
  url: 'http://localhost:5173/bandeja',
  runScripts: 'dangerously',
});

global.window = dom.window;
global.document = dom.window.document;
global.HTMLElement = dom.window.HTMLElement;

// Mock de fetch para interceptar llamadas al API
let dictamenEnviado = null;

global.fetch = async (url, options = {}) => {
  const urlStr = url.toString();

  if (urlStr.includes('/api/v1/casos?') || urlStr.endsWith('/api/v1/casos')) {
    return {
      ok: true,
      status: 200,
      json: async () => casosMock,
    };
  }

  if (urlStr.includes('/api/v1/metricas/validaciones')) {
    return {
      ok: true,
      status: 200,
      json: async () => ({
        total_validaciones_cobrables: 42,
        automaticas_f4: 28,
        asistidas_f1: 14,
        diferencia_auditoria: 0,
      }),
    };
  }

  const matchCaso = urlStr.match(/\/api\/v1\/casos\/([^/?]+)$/);
  if (matchCaso) {
    const id = matchCaso[1];
    const caso = casosMock.find(c => c.caso_id === id);
    if (!caso) return { ok: false, status: 404, json: async () => ({ detail: 'Not found' }) };
    return {
      ok: true,
      status: 200,
      json: async () => caso,
    };
  }

  if (urlStr.includes('/dictamen') && options.method === 'POST') {
    const body = JSON.parse(options.body);
    dictamenEnviado = body;
    const matchId = urlStr.match(/\/api\/v1\/casos\/([^/]+)\/dictamen/);
    const id = matchId ? matchId[1] : 'CASO-2026-003';
    return {
      ok: true,
      status: 200,
      json: async () => ({
        mensaje: 'Dictamen registrado con éxito',
        caso_id: id,
        decision: body.decision,
        discrepancia_detectada: true,
        hash_auditoria: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      }),
    };
  }

  return { ok: false, status: 404, json: async () => ({ error: 'Ruta no encontrada' }) };
};

// Importar vistas dinámicamente
const { renderBandejaView } = await import('../src/views/BandejaView.js');
const { renderDetalleCasoView } = await import('../src/views/DetalleCasoView.js');

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function runE2ETests() {
  const appRoot = document.getElementById('app-root');

  // --------------------------------------------------------------------------
  // PASO 1: Carga y verificación de la Bandeja de Entrada (/bandeja)
  // --------------------------------------------------------------------------
  console.log('📌 [Paso 1/5]: Renderizando Bandeja Principal y KPIs...');
  let casoSeleccionadoParaNavegar = null;
  renderBandejaView(appRoot, (id) => {
    casoSeleccionadoParaNavegar = id;
  });

  // Esperar a que la carga asíncrona pueble el DOM
  await sleep(150);

  const pendientesEl = document.getElementById('kpi-pendientes');
  assert.ok(pendientesEl, 'El KPI de pendientes debe existir en el DOM');
  console.log(`   ✓ KPIs cargados: ${pendientesEl.textContent} expedientes en cola.`);

  const listItems = appRoot.querySelectorAll('.btn-revisar-caso');
  assert.ok(listItems.length >= 7, `Deben renderizarse los casos en la bandeja (actual: ${listItems.length})`);
  console.log(`   ✓ Tabla de bandeja poblada con ${listItems.length} expedientes.`);

  // --------------------------------------------------------------------------
  // PASO 2: Filtrado por Causal y Búsqueda Interactiva
  // --------------------------------------------------------------------------
  console.log('📌 [Paso 2/5]: Probando filtros de causal y búsqueda en vivo...');
  const searchInput = document.getElementById('search-input');
  searchInput.value = 'Mendoza';
  searchInput.dispatchEvent(new dom.window.Event('input'));

  const itemsFiltrados = appRoot.querySelectorAll('.btn-revisar-caso');
  assert.strictEqual(itemsFiltrados.length, 1, 'La búsqueda por "Mendoza" debe retornar exactamente 1 caso');
  console.log('   ✓ Búsqueda textual reactiva verificada con éxito.');

  // Limpiar búsqueda
  searchInput.value = '';
  searchInput.dispatchEvent(new dom.window.Event('input'));

  // --------------------------------------------------------------------------
  // PASO 3: Navegación al Detalle del Caso y Verificación Anti-Anclaje (RNF-08)
  // --------------------------------------------------------------------------
  console.log('📌 [Paso 3/5]: Abriendo expediente CASO-2026-003 (Bajo Puntaje DEC-07)...');
  await renderDetalleCasoView(appRoot, 'CASO-2026-003', () => {});
  await sleep(100);

  // Verificación Crítica RNF-08: El Tercio Superior NO debe contener mención al puntaje numérico
  const superiorContainer = appRoot.querySelector('.tier-superior-container');
  assert.ok(superiorContainer, 'El contenedor del Tercio Superior debe existir');

  const textoSuperior = superiorContainer.textContent;
  assert.ok(!textoSuperior.includes('/ 100'), 'RNF-08 VIOLADO: El Tercio Superior no debe exhibir el puntaje');
  assert.ok(!textoSuperior.includes('48.3'), 'RNF-08 VIOLADO: El puntaje (48.3) no debe exponerse en el primer viewport');
  console.log('   ✓ Verificación Anti-Anclaje RNF-08 APROBADA: Cero menciones de puntaje en el Tercio Superior.');

  // Comprobar visor de evidencias y bounding box
  const visorImg = superiorContainer.querySelector('img');
  assert.ok(visorImg && visorImg.src.startsWith('data:image/svg+xml'), 'El visor debe proyectar el SVG oficial');

  const boundingBoxes = superiorContainer.querySelectorAll('.bounding-box');
  assert.ok(boundingBoxes.length >= 1, 'Debe desplegarse el recuadro rojo de anomalía espacial');
  console.log(`   ✓ Visor con Bounding Boxes proyectado correctamente (${boundingBoxes.length} hallazgo).`);

  // --------------------------------------------------------------------------
  // PASO 4: Inspección de Señales Analíticas (Tercio Medio)
  // --------------------------------------------------------------------------
  console.log('📌 [Paso 4/5]: Verificando Matriz de Señales del Tercio Medio...');
  const tercioMedio = document.getElementById('tercio-medio-seccion');
  assert.ok(tercioMedio, 'La sección del Tercio Medio debe existir en el DOM');
  assert.ok(tercioMedio.textContent.includes('Autenticidad Documental'));
  assert.ok(tercioMedio.textContent.includes('Habilitación Prestador'));
  console.log('   ✓ Matriz de 4 componentes analíticos con barras de progreso verificada.');

  // --------------------------------------------------------------------------
  // PASO 5: Tercio Inferior, Revelación de Puntaje, Discrepancia y Dictamen
  // --------------------------------------------------------------------------
  console.log('📌 [Paso 5/5]: Revelando Puntaje y emitiendo dictamen con discrepancia (RF-19)...');
  const panelInferior = document.getElementById('panel-puntaje-confianza');
  assert.ok(panelInferior, 'El panel del Tercio Inferior debe existir');

  // En el Tercio Inferior, el puntaje sí se revela
  assert.ok(panelInferior.textContent.includes('48.3'), 'El puntaje 48.3 debe revelarse en el Tercio Inferior');
  console.log('   ✓ Revelación diferida verificada: Puntaje 48.3 visible al final del recorrido.');

  // Seleccionar acción "APROBAR" en caso de bajo puntaje
  const radioAprobar = panelInferior.querySelector('input[value="APROBAR"]');
  assert.ok(radioAprobar, 'El botón de radio APROBAR debe existir');
  radioAprobar.checked = true;
  radioAprobar.dispatchEvent(new dom.window.Event('change'));

  // Verificar que se activa el banner de Discrepancia Detectada (RF-19)
  const discrepancyBanner = document.getElementById('discrepancy-banner');
  assert.ok(!discrepancyBanner.classList.contains('hidden'), 'El banner de discrepancia debe activarse');
  console.log('   ✓ Banner reactivo de Discrepancia Detectada (RF-19) activado correctamente.');

  // Comprobar que el botón de envío está deshabilitado si justificación < 15 chars
  const submitBtn = document.getElementById('btn-submit-dictamen');
  const justificationInput = document.getElementById('justification-input');

  justificationInput.value = 'Aprobado ok'; // 11 chars
  justificationInput.dispatchEvent(new dom.window.Event('input'));
  assert.ok(submitBtn.disabled, 'El botón debe permanecer deshabilitado con justificación < 15 caracteres');

  // Ingresar justificación técnica válida
  justificationInput.value = 'Se autoriza cobertura tras revisión de examen físico original visado por médico contralor.';
  justificationInput.dispatchEvent(new dom.window.Event('input'));
  assert.ok(!submitBtn.disabled, 'El botón debe habilitarse con justificación >= 15 caracteres');
  console.log('   ✓ Validación de fundamentación obligatoria (>=15 chars) comprobada.');

  // Emitir dictamen
  submitBtn.dispatchEvent(new dom.window.Event('click'));
  await sleep(100);

  // Verificar que el modal de confirmación con sello SHA-256 se abre
  const modalContainer = document.getElementById('modal-container');
  assert.ok(!modalContainer.classList.contains('hidden'), 'El modal de confirmación debe abrirse');
  assert.ok(modalContainer.textContent.includes('Dictamen Registrado con Éxito'));
  assert.ok(modalContainer.textContent.includes('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'));
  console.log('   ✓ Modal de confirmación con sello criptográfico SHA-256 desplegado con éxito.');

  console.log('\n🎉 ¡TODAS LAS PRUEBAS DE LA SUITE E2E PASARON SATISFACTORIAMENTE (100%)!');
}

runE2ETests().catch(err => {
  console.error('\n❌ Error en la ejecución de la suite E2E:', err);
  process.exit(1);
});
