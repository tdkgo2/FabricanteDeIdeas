# BITACORA — Fabricante de Ideas

**Última actualización:** 2026-10-21 · **Última sesión:** `docs/bitacora/261021_sesion.md` · **Actualizado por:** Tomek + Claude

Único documento de estado que se reescribe, siempre completo. Solo lo vigente y lo pendiente; lo que
pasó vive en `docs/bitacora/`. Tope: 30 KB.

---

## 1. Vigente

**Proyecto**
- **Fabricante de Ideas**: guarda el kit de proyecto y acompaña la creación de proyectos nuevos.
- Repo privado `tdkgo2/FabricanteDeIdeas`. Carpeta en el Pi: `~/proyectos/FabricanteDeIdeas` (solo
  guarda el repo; aquí no corre nada). Project de claude.ai: "Fabricante de Ideas".
- Sin Claude Code (Tomek, 21-10): los cambios se entregan como archivos y Tomek los comitea.

**Kit vigente: v2.0** (`kit/`, 2026-10-21)
- Origen: Trama (`CdL_Trama`, `main` en `bdd1b7d`, 19-10).
- Trae: instrucciones del Project, `CLAUDE.md` con 16 reglas duras, `PROCESO.md` v2, BITACORA corta
  con sesiones fechadas write-once, guía del día 0, cierre de sesión, seis plantillas, guardián v2
  parametrizado (76 pruebas), `cc.sh`, `cerrar_code.sh` por carpeta e `instanciar.sh`.
- Correcciones ya incluidas, salidas del día 0 de CronosLFT: `cerrar_code.sh` no lista el servidor
  de tmux; la limpieza de la rama de prueba suelta primero el árbol de Code y borra la rama local
  además de la remota.

**Proyectos creados**: registro en `docs/PROYECTOS.md`.

**Decisiones vigentes**
- 2026-10-21: el kit vive en su propio repo y Project; ningún proyecto lleva la creación de otro.
- 2026-10-21: en el Pi, cada proyecto en `~/proyectos/<Nombre>` con su guardián en `~/.<slug>/`.

---

## 2. Infraestructura

Usa el Orange Pi 5 de Tomek (usuario `orangepi`, LAN `192.168.1.163`, Tailscale `100.97.168.28`)
solo para guardar el repo y para instanciar el kit. Claude Code del Pi pidió `/login` el 21-10
(sesión de claude.ai vencida): el día 0 de cada proyecto lo comprueba antes de la prueba en vivo.

---

## 3. Pendientes

**Kit v2.1** (lo que enseñó el día 0 de CronosLFT)
1. `instanciar.sh` deja una carpeta `para_knowledge/` plana con los archivos exactos que se suben,
   y las instrucciones del Project ya listas para pegar.
2. `instanciar.sh` genera el mensaje de traspaso con los datos del proyecto (los resultados del día 0
   se agregan al final).
3. La guía pone el Knowledge del Project nuevo **antes** del traspaso. El 21-10 fue al revés y el
   Project de CronosLFT tuvo que detenerse.
4. El paso B de la guía comprueba la sesión de Claude Code (`Not logged in` salió en medio de la prueba).
5. El paso E dice qué contestarle a Code cuando, en la prueba, se niega por su cuenta sin intentar el
   comando: lo que se prueba es el guardián.

**Revisores en GitHub** (vale para todos los proyectos)
- En un repo de cuenta personal, todo colaborador puede escribir. Para un revisor de solo lectura,
  los repos van en una organización de GitHub (gratis, rol Read). Tomek decide si crea la
  organización y mueve ahí los repos (CronosLFT lo trata en su ADR de roles).

**Trama**
- En su próximo cierre, una línea: de Trama salió el kit v2.0 (21-10). Y anotar que la
  configuración de su Project muestra otra vez una fuente de GitHub (`CdL_Trama`, `main`), aunque su
  BITACORA dice que la sincronización desapareció el 06-10.

---

## 4. Sesiones recientes
- `261021_sesion.md` — kit v2.0 construido desde Trama; día 0 de CronosLFT; nace Fabricante de Ideas.
