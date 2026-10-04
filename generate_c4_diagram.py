import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up figure with high DPI for publication quality
plt.style.use('default')
fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
ax.set_xlim(0, 140)
ax.set_ylim(0, 100)
ax.axis('off')

# Colors - C4 Standard Palette
PERSON_COLOR = '#08427B'       # Dark Navy
CONTAINER_COLOR = '#1168BD'    # Primary Blue
DB_COLOR = '#1C7CD6'           # Secondary Blue for DB
BOUNDARY_COLOR = '#4A5568'     # Slate Grey
BG_COLOR = '#FFFFFF'
TEXT_WHITE = '#FFFFFF'
TEXT_MUTED = '#E2E8F0'

# Title
ax.text(70, 96, "Diagrama de Contenedores C4 — Plataforma MIRA", 
        ha='center', va='center', fontsize=18, fontweight='bold', color='#0F172A')
ax.text(70, 93, "Nivel 2 del Modelo C4: Incremento Funcional de F4 (Motor de Umbrales) y F1 (Bandeja Asistida)", 
        ha='center', va='center', fontsize=11, style='italic', color='#475569')

# 1. PERSON: Operador de Liquidación
# Head
circle = patches.Circle((22, 79), 3.2, facecolor=PERSON_COLOR, edgecolor='#052B52', linewidth=1.5, zorder=3)
ax.add_patch(circle)
# Body box
person_box = patches.FancyBboxPatch((7, 60), 30, 14, boxstyle="round,pad=0.8,rounding_size=2",
                                    facecolor=PERSON_COLOR, edgecolor='#052B52', linewidth=1.5, zorder=3)
ax.add_patch(person_box)
ax.text(22, 69, "Operador de Liquidación", ha='center', va='center', fontsize=10.5, fontweight='bold', color=TEXT_WHITE, zorder=4)
ax.text(22, 66, "[Persona / Perito Humano]", ha='center', va='center', fontsize=8.5, color=TEXT_MUTED, zorder=4)
ax.text(22, 63, "Examina evidencias en F1,\nrevisa alertas y emite dictamen.", ha='center', va='center', fontsize=7.5, color=TEXT_WHITE, zorder=4)

# 2. SYSTEM BOUNDARY: Plataforma MIRA
boundary = patches.FancyBboxPatch((47, 6), 88, 81, boxstyle="round,pad=1.2,rounding_size=3",
                                  facecolor='#F8FAFC', edgecolor=BOUNDARY_COLOR, linewidth=1.8, linestyle='--', zorder=1)
ax.add_patch(boundary)
ax.text(49, 84, "  Sistema MIRA (Límite del Incremento F4 + F1)  ", ha='left', va='center', 
        fontsize=11.5, fontweight='bold', color='#1E293B', backgroundcolor='#E2E8F0', zorder=2)

# Helper function for C4 containers
def draw_container(ax, x, y, w, h, title, tech, desc, is_db=False):
    if is_db:
        # Cylinder top & body
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=2",
                                     facecolor='#0284C7', edgecolor='#0369A1', linewidth=1.5, zorder=3)
        ax.add_patch(box)
        db_badge = patches.Ellipse((x + w/2, y + h), w*0.7, 2.5, facecolor='#38BDF8', edgecolor='#0369A1', linewidth=1.2, zorder=4)
        ax.add_patch(db_badge)
        tag = "[Base de Datos]"
    else:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=2",
                                     facecolor=CONTAINER_COLOR, edgecolor='#0C4A6E', linewidth=1.5, zorder=3)
        ax.add_patch(box)
        tag = "[Contenedor]"

    ax.text(x + w/2, y + h - 2.8, title, ha='center', va='center', fontsize=10, fontweight='bold', color=TEXT_WHITE, zorder=5)
    ax.text(x + w/2, y + h - 5.2, f"{tag}: {tech}", ha='center', va='center', fontsize=7.8, style='italic', color='#BAE6FD', zorder=5)
    ax.text(x + w/2, y + (h - 7)/2, desc, ha='center', va='center', fontsize=7.5, color=TEXT_WHITE, zorder=5)

# Container 1: F1 SPA
draw_container(ax, 52, 60, 36, 17, 
               "Bandeja Asistida (F1)", 
               "Vite, Vanilla JS, Tailwind CSS", 
               "SPA web interactiva con Embudo de 3 Tercios,\nvisor documental SVG con bounding boxes\ny panel resolutivo con captura de discrepancias.")

# Container 2: API Gateway BFF
draw_container(ax, 95, 60, 36, 17, 
               "API Gateway y BFF", 
               "FastAPI / Uvicorn (Python 3.12)", 
               "Expone endpoints REST OpenAPI, aplica\nmiddleware Leaky Bucket (0% descartes)\ny validación de aislamiento multitenant.")

# Container 3: Core F4
draw_container(ax, 95, 34, 36, 17, 
               "Motor de Dominio (F4)", 
               "Python 3.12 (Arquitectura Hexagonal)", 
               "Calcula puntajes ponderados ($0-100$), aplica reglas\nde corte por mínimos (RF-11 / H-12), cortocircuito\npor fraude (RF-12) y prohíbe rechazos (DEC-07).")

# Container 4: Persistencia Local
draw_container(ax, 52, 10, 36, 15, 
               "Persistencia Local (Fallback C4)", 
               "JSON Estructurado (Atómico)", 
               "Repositorio local desacoplado (LocalJsonRepository)\npara levantamiento autónomo en <5 s sin credenciales.", 
               is_db=True)

# Container 5: Persistencia Cloud
draw_container(ax, 95, 10, 36, 15, 
               "Persistencia Cloud (Firestore)", 
               "Google Cloud Firestore SDK", 
               "Almacén NoSQL distribuido para expedientes,\nrastro forense SHA-256 (DEC-10) y métricas.", 
               is_db=True)

# Container 6: Inyector Canónico (Seed)
draw_container(ax, 10, 16, 28, 14, 
               "Inyector Sintético (Seed)", 
               "Python CLI (seed_dataset.py)", 
               "Carga 8 casos canónicos de prueba\ncon evidencias médicas SVG sintéticas.")

# Helper function for Arrows with labels
def draw_arrow(ax, start, end, label, text_offset=(0, 0), connectionstyle="arc3,rad=0", ha='center'):
    arrow = patches.FancyArrowPatch(start, end,
                                    connectionstyle=connectionstyle,
                                    arrowstyle='-|>,head_length=5,head_width=3',
                                    color='#0284C7', linewidth=1.6, zorder=2)
    ax.add_patch(arrow)
    mid_x = (start[0] + end[0]) / 2 + text_offset[0]
    mid_y = (start[1] + end[1]) / 2 + text_offset[1]
    bbox_props = dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#CBD5E1", lw=0.8, alpha=0.95)
    ax.text(mid_x, mid_y, label, ha=ha, va='center', fontsize=7.2, color='#1E293B', fontweight='semibold', bbox=bbox_props, zorder=6)

# Arrows
# Operador -> SPA
draw_arrow(ax, (37, 68), (52, 68), "1. Inspecciona boletas\ny emite dictamen\n[HTTPS / UI]", text_offset=(0, 0))

# SPA -> API Gateway
draw_arrow(ax, (88, 68), (95, 68), "2. Consume casos y\nenvía resoluciones\n[REST / JSON]", text_offset=(0, 0))

# API Gateway -> Core F4
draw_arrow(ax, (113, 60), (113, 51), "3. Invoca evaluación\n[Llamada de Dominio]", text_offset=(0, 0))

# Core F4 -> Persistencia Local
draw_arrow(ax, (100, 34), (80, 25), "4a. Guarda expediente\n[Modo Local JSON]", text_offset=(-6, 1), connectionstyle="arc3,rad=-0.1")

# Core F4 -> Persistencia Cloud
draw_arrow(ax, (113, 34), (113, 25), "4b. Sincroniza rastro\n[Firestore SDK]", text_offset=(0, 0))

# SPA -> Persistencia Local (Polling / read)
draw_arrow(ax, (68, 60), (68, 25), "5. Consulta expedientes\ny SLA [Adaptador]", text_offset=(0, 0))

# Seed -> Persistencia Local
draw_arrow(ax, (38, 18), (52, 18), "Inyecta dataset\ncanónico [CLI]", text_offset=(0, 0))

# Footer Note
ax.text(70, 2.5, "Diseño conforme a las reglas del Capítulo 4.2 y decisiones vinculantes DEC-01 a DEC-09 del Representante del Cliente.",
        ha='center', va='center', fontsize=8, color='#64748B')

plt.tight_layout()
plt.savefig("c4_contenedores_mira.png", dpi=300, bbox_inches='tight')
print("Diagrama guardado exitosamente como c4_contenedores_mira.png")
