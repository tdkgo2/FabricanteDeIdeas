# BITACORA — {{NOMBRE}}

**Última actualización:** {{FECHA}} · **Última sesión:** `docs/bitacora/{{AAMMDD}}_sesion.md` · **Actualizado por:** {{LIDER}} + Claude (Project)

Único documento de estado que se reescribe, siempre completo. Solo lo vigente y lo pendiente;
lo que pasó vive en `docs/bitacora/` y lo decidido para siempre en un ADR. Tope: 30 KB.
Reglas completas: `docs/PROCESO.md` §9.

---

## 1. Vigente

**Proyecto**
- Nombre: **{{NOMBRE}}** ({{DESCRIPCION_CORTA}}). Repo privado `{{CUENTA_GITHUB}}/{{REPO}}`. Carpeta en {{DISPOSITIVO}}: `~/{{RUTA}}` (Code) y `~/{{RUTA}}_main` (worktree de `main`). Paquete / slug: `{{SLUG}}`.
- Project de claude.ai: "{{PROJECT_CLAUDE}}". Revisor: {{REVISOR}}.
- Proceso: `docs/PROCESO.md` v2.1 (kit de proyecto). Cierre: `docs/CIERRE_SESION.md`.

**Documentos que mandan**
- Maestros: ninguno todavía.
- ADR: ninguno todavía. Índice: `docs/adr/INDICE_ADR.md`.

**Decisiones vigentes sin ADR** (una línea cada una, con fecha)
- {{FECHA}}: el proyecto arranca con el kit de proyecto v2.1 (origen: Trama).
- {{FECHA}}: Knowledge por la fuente de GitHub (`CLAUDE.md` y `docs/` de `main`); «Sync now» es el último paso de cada cierre.

**Archivos de datos**: registro en `docs/datos/REGISTRO_DATOS.md`. Ninguno todavía.

---

## 2. Infraestructura — {{DISPOSITIVO}}

Usuario `{{USUARIO_DISPOSITIVO}}`, LAN `{{IP_LAN}}` (SSH y `scp` del líder), Tailscale `{{IP_TAILSCALE}}`.

**Hecho**
- (nada todavía; el día 0 está en `docs/GUIA_DIA_0.md`)

**Pendiente**
- Día 0: pasos A a I de `docs/GUIA_DIA_0.md`.

---

## 3. Pendientes

**Plan (en orden)**
1. Día 0 (`docs/GUIA_DIA_0.md`, pasos A a I).
2. Primeros ADR del proyecto (`docs/GUIA_DIA_0.md` §J): stack, bases y roles, red, respaldo, datos permitidos en el equipo.
3. Llenar las secciones `[LLENAR` de `CLAUDE.md` con lo que digan esos ADR.
4. T-001 (esqueleto del stack, Makefile parte 2, guarda de la suite, base de prueba).

**Decisiones abiertas**
- (ninguna)

---

## 4. Sesiones recientes (las tres últimas; todas en `docs/bitacora/`)
- `{{AAMMDD}}_sesion.md` — arranque con el kit de proyecto.
