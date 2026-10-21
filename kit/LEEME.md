# Kit de proyecto v2.1

Forma de trabajo para construir software con cuatro partes: un **líder** que decide, un **Project de
claude.ai** que coordina y diseña, **Claude Code** que programa en un equipo propio, y un **revisor**
externo. Sale de Trama (CdL_Trama, septiembre–octubre 2026): lo que ahí se aprendió a golpes aquí ya
viene puesto desde el día 1.

El kit define **cómo se trabaja**, no **qué se construye**: el stack, el modelo y las reglas del dominio
los deciden los primeros ADR de cada proyecto.

## Qué trae
```
LEEME.md                  este archivo
valores.ejemplo.env       los datos del proyecto nuevo (nombre, repo, carpeta, equipo, descargas…)
instanciar.sh             crea el repo nuevo a partir de repo/ y la carpeta _arranque con esos valores
arranque/traspaso.txt     plantilla del mensaje de traspaso al Project nuevo
repo/                     el repo tal como nace
  CLAUDE.md               reglas para Claude Code (16 reglas duras + secciones [LLENAR])
  README.md · Makefile · .gitignore
  .claude/settings.json   hook del guardián + recordatorio de fin de sesión
  docs/PROCESO.md         cómo se trabaja: partes, ciclo, banderas, merge, guardián, bases, Knowledge
  docs/BITACORA.md        estado vigente (corta, tope 30 KB)
  docs/bitacora/          una sesión por archivo, write-once
  docs/CIERRE_SESION.md   pasos y comandos del cierre (el último: «Sync now»)
  docs/GUIA_DIA_0.md      puesta en marcha en el equipo, paso a paso
  docs/proyecto/          instrucciones y descripción para el Project de claude.ai
  docs/adr/INDICE_ADR.md  índice con estado y vigencia
  docs/plantillas/        adr, tarea, cierre, reconocimiento, parcial, sesión
  docs/datos/REGISTRO_DATOS.md
  scripts/cc.sh           arranca Code en tmux + Remote Control
  scripts/cerrar_code.sh  cierra solo las sesiones de Code de este proyecto
  scripts/guardian/       el guardián (fuente)
  tests/test_guardian.py  76 pruebas del guardián en sandbox
```

## Cómo se crea un proyecto
Lo acompaña el Project "Fabricante de Ideas"; el kit vive en su repo, en el equipo:
`~/proyectos/FabricanteDeIdeas/kit`.
1. **Equipo (SSH): los valores.** El Project escribe el archivo completo y se crea con un heredoc en
   `~/valores_<slug>.env`, fuera de cualquier repo (el Bloc de notas de Windows agrega `.txt` y un
   carácter invisible al inicio). `DESCARGAS` es la carpeta propia del proyecto en la laptop.
2. **Equipo (SSH): instanciar.**
   ```bash
   cd ~/proyectos/FabricanteDeIdeas
   git pull
   bash kit/instanciar.sh ~/valores_<slug>.env
   ```
   Crea `~/<RUTA>` (el repo) y `~/<RUTA>_arranque` (instrucciones, descripción y traspaso para el
   Project), y termina con "marcadores sin valor: 0". Si queda alguno, dice cuál.
3. **Sigue `docs/GUIA_DIA_0.md`** dentro del repo nuevo: carpeta de descargas, equipo, primer push,
   worktree de `main`, guardián, prueba de Code, Project de claude.ai (Knowledge por GitHub **antes**
   del traspaso), revisor.
4. **Primera sesión del Project:** los primeros ADR (§J de la guía) y, con ellos, las secciones
   `[LLENAR` de `CLAUDE.md`. Luego T-001.

## Lo que ya viene resuelto (y por qué)
| En el kit | Lo que pasó en Trama (o en CronosLFT) |
|---|---|
| BITACORA corta + sesiones fechadas write-once | La BITACORA llegó a 207 KB y se leía entera en cada sesión. |
| Base y web de prueba exigidas desde el día 1 | Llegaron en la tarea 15; antes el humo corría contra copias sueltas. |
| Rol de la aplicación sin superusuario desde el día 1 | El rol de Trama siguió siendo superusuario; el ADR que lo corregía quedó para después. |
| La suite solo corre con `make test` y una guarda | Un `pytest` a secas escribió dos veces en producción (con rollback). |
| La FASE 0 no corre la suite | Ese `pytest` salió de la plantilla de reconocimiento. |
| Restauración de prueba programada del respaldo | Trama solo validaba el índice del dump y nunca agendó una restauración. |
| Guardián v2 fuera del árbol, congelado | El guardián dentro del repo cambiaba con la rama; tomó tres vueltas dejarlo bien. |
| `.env*.example` y `~/.claude/plans/` permitidos | Falsos positivos del guardián en T-015. |
| Push "escrito solo", y el mensaje lo dice | Un push con `\| tail` o `--set-upstream` se bloqueaba sin explicar por qué. |
| `cerrar_code.sh` por carpeta | `pkill -f -- '--sdk-url'` mata las sesiones de todos los proyectos del equipo. |
| Merge y push de `main` solo del líder, desde `<RUTA>_main` | `main` no se puede abrir en el árbol de Code mientras tiene una rama. |
| ADR sin números reservados, índice con vigencia | Trama llegó a 59 ADR con tres reservados sin redactar y muchos ya históricos. |
| "Estado de trabajos" de una línea por tarea | Las filas de Trama crecieron a párrafos. |
| Instrucciones del Project versionadas en git | Vivían solo en la configuración del Project. |
| Knowledge por la fuente de GitHub (`CLAUDE.md` y `docs/`), «Sync now» al final de cada cierre, nada subido a mano | La sincronización no se actualiza sola: la copia de Trama estuvo 13 días atrasada; y con copias manuales al lado, la búsqueda mezclaba versiones. |
| Knowledge del Project nuevo antes del traspaso | CronosLFT: el traspaso llegó con el Knowledge vacío y el Project tuvo que detenerse. |
| Carpeta `_arranque` y traspaso generados por `instanciar.sh` | CronosLFT: instrucciones y traspaso se armaron a mano en el día 0. |
| Carpeta de descargas por proyecto | Las BITACORA y sesiones de varios proyectos se juntaban en `D:\Descargas` con el mismo nombre. |
| El paso B comprueba la sesión de Claude Code | CronosLFT: `Not logged in` apareció en medio de la prueba del guardián. |
| El paso B apaga lo que escucha en la red sin uso | La imagen del Orange Pi traía adbd (5555) y xrdp (3389) abiertos. |
| El paso E dice qué contestar si Code se niega sin intentar | CronosLFT: lo que se prueba es el guardián, no la prudencia de Code. |
| Tareas para Sonnet | Code no puede usar Opus en la cuenta. |
| Una conversación del Project por tarea o revisión | Las conversaciones largas gastaban el uso semanal. |
| `REGISTRO_DATOS` con SHA-256 | Un archivo generado en el Project se perdió dos sesiones. |

## Cambios del kit
- **v2.1 (2026-10-21)** — lo que enseñaron el día 0 de CronosLFT y Trama el mismo día:
  - Knowledge por la fuente de GitHub (`CLAUDE.md` y `docs/` de `main`), «Sync now» como último paso
    del cierre, nada subido a mano, verificación al iniciar; plan B: copia manual sin fuente (PROCESO
    §10, CIERRE paso 7, instrucciones del Project). Cada sesión anota el hash del cierre anterior.
  - `instanciar.sh` crea `~/<RUTA>_arranque/` con `instrucciones.txt`, `descripcion.txt` y
    `traspaso.txt`; la guía pone el Knowledge antes del traspaso (§G).
  - `DESCARGAS` es la carpeta propia del proyecto; la guía la crea (§A).
  - Paso B: comprueba la sesión de Claude Code y apaga los servicios que escuchan en la red sin uso.
  - Paso C: la investigación previa entra al repo como `docs/proyecto/INVESTIGACION_PREVIA.md`.
  - Paso E: qué contestarle a Code si se niega sin intentar el comando.
  - PROCESO §7: restauración de prueba programada del respaldo.
  - Este LEEME: el kit vive en el repo de Fabricante de Ideas y los valores en `~/valores_<slug>.env`.
- **v2.0 (2026-10-21)** — primera versión, a partir de Trama al 2026-10-19 (`main` en `bdd1b7d`).

Un aprendizaje nuevo en un proyecto que sirva para todos se anota en su sesión y, cuando se juntan
varios, sale una versión nueva del kit.
