/**
 * Controlador Principal y Enrutador SPA de la Plataforma MIRA (F1).
 */

import { renderBandejaView } from './views/BandejaView.js';
import { renderDetalleCasoView } from './views/DetalleCasoView.js';

const appRoot = document.getElementById('app-root');

function navegarHacia(ruta, push = true) {
  if (push) {
    window.history.pushState({}, '', ruta);
  }

  // Desplazar al tope
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Enrutamiento simple
  if (ruta.startsWith('/bandeja/') && ruta.length > 9) {
    const casoId = ruta.replace('/bandeja/', '');
    renderDetalleCasoView(appRoot, casoId, () => navegarHacia('/bandeja'));
  } else {
    renderBandejaView(appRoot, (casoId) => {
      navegarHacia(`/bandeja/${casoId}`);
    });
  }
}

// Escuchar cambios de historial en el navegador (Botones Atrás / Adelante)
window.addEventListener('popstate', () => {
  navegarHacia(window.location.pathname, false);
});

// Inicialización de la aplicación
document.addEventListener('DOMContentLoaded', () => {
  const rutaInicial = window.location.pathname === '/' ? '/bandeja' : window.location.pathname;
  navegarHacia(rutaInicial, false);
});
