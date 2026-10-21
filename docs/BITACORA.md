# BITACORA — Fabricante de Ideas

**Última actualización:** 2026-10-21 (2) · **Última sesión:** `docs/bitacora/261021_2_sesion.md` · **Actualizado por:** Tomek + Claude

Único documento de estado que se reescribe, siempre completo. Solo lo vigente y lo pendiente; lo que
pasó vive en `docs/bitacora/`. Tope: 30 KB.

---

## 1. Vigente

**Proyecto**
- **Fabricante de Ideas**: guarda el kit de proyecto y acompaña la creación de proyectos nuevos.
- Repo privado `tdkgo2/FabricanteDeIdeas`. Carpeta en el Pi: `~/proyectos/FabricanteDeIdeas` (solo
  guarda el repo; aquí no corre nada). Project de claude.ai: "Fabricante de Ideas".
- Sin Claude Code (Tomek, 21-10): los cambios se entregan como archivos y Tomek los comitea.
- Knowledge: fuente de GitHub, rama `main`, `docs/` y `kit/`; «Sync now» es el último paso de cada
  cierre. Lo que está bajo `kit/` son plantillas, no documentos de este Project.
- Descargas de este Project: `D:\Descargas\FabricanteDeIdeas`.

**Kit vigente: v2.1** (`kit/`, 2026-10-21)
- Origen: Trama (`CdL_Trama`, `main` en `bdd1b7d`, 19-10). v2.0 el 21-10; v2.1 el mismo día con lo
  que enseñaron el día 0 de CronosLFT y Trama (lista en `kit/LEEME.md`).
- Trae: instrucciones del Project, `CLAUDE.md` con 16 reglas duras, `PROCESO.md` v2.1, BITACORA corta
  con sesiones fechadas write-once, guía del día 0, cierre con «Sync now», seis plantillas, guardián v2
  parametrizado (76 pruebas), `cc.sh`, `cerrar_code.sh` por carpeta, `instanciar.sh` con la carpeta
  `_arranque` (instrucciones, descripción y traspaso).
- Probado el 21-10 instanciando en carpeta temporal: 0 marcadores, 76 pruebas, `bash -n` de los
  cuatro scripts, pasos C, D y limpieza del E ensayados contra un remoto local.

**Proyectos creados**: registro en `docs/PROYECTOS.md`.

**Decisiones vigentes**
- 2026-10-21: el kit vive en su propio repo y Project; ningún proyecto lleva la creación de otro.
- 2026-10-21: en el Pi, cada proyecto en `~/proyectos/<Nombre>` con su guardián en `~/.<slug>/`.
- 2026-10-21: Knowledge de cada Project por la fuente de GitHub (`CLAUDE.md` y `docs/` de `main`),
  sin copias a mano. Si un proyecto quiere su BITACORA escrita directo en el Knowledge, lo decide él.
- 2026-10-21: los nombres genéricos (`BITACORA.md`, `CLAUDE.md`) se mantienen; los proyectos se
  separan por carpeta de descargas y por fuente única de Knowledge.
- 2026-10-21: la investigación previa de un proyecto entra al repo como
  `docs/proyecto/INVESTIGACION_PREVIA.md`, sin datos personales reales.

---

## 2. Infraestructura

Usa el Orange Pi 5 de Tomek (usuario `orangepi`, LAN `192.168.1.163`, Tailscale `100.97.168.28`)
solo para guardar el repo y para instanciar el kit. Los valores de cada proyecto nuevo van en
`~/valores_<slug>.env`.
- 21-10: Claude Code del Pi pidió `/login` (sesión vencida); desde la v2.1, el paso B lo comprueba.
- 21-10: adbd (5555, `usbdevice.service`) y xrdp (3389) apagados en el Pi (lo hizo Trama).

---

## 3. Pendientes

**Al terminar este cierre**
- Mensaje a CronosLFT: Knowledge por la fuente de GitHub y restauración de prueba para su ADR de
  respaldo. Borrador en `docs/bitacora/261021_2_sesion.md`; Tomek lo revisa y lo manda.

**Para el próximo día 0**
- Comprobar que la interfaz deja seleccionar `CLAUDE.md` suelto en la fuente de GitHub (Trama midió
  que no deja excluir un archivo suelto). Si no deja, raíz con exclusiones y se ajusta la guía §G.

**Revisores en GitHub** (vale para todos los proyectos)
- En un repo de cuenta personal, todo colaborador puede escribir. Para un revisor de solo lectura,
  los repos van en una organización de GitHub (gratis, rol Read). Tomek decide si crea la
  organización y mueve ahí los repos (CronosLFT lo trata en su ADR de roles).

---

## 4. Sesiones recientes
- `261021_2_sesion.md` — kit v2.1 (Knowledge por GitHub, carpeta `_arranque`, traspaso, guía B/C/E/G,
  restauración de prueba); este Project pasa a la fuente de GitHub.
- `261021_sesion.md` — kit v2.0 construido desde Trama; día 0 de CronosLFT; nace Fabricante de Ideas.
