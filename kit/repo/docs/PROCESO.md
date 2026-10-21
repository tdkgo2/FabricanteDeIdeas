# PROCESO — cómo se trabaja en {{NOMBRE}}

Versión 2.1 del kit de proyecto ({{FECHA}}). Origen: el modelo Project ⇄ Claude Code ⇄ decisor
que se usó en Trama (CdL_Trama, septiembre–octubre 2026), con lo que se aprendió ahí ya incorporado.
Este documento cambia poco; lo que cambia cada semana vive en `docs/BITACORA.md`.

## 1. Partes

| Parte | Qué hace | Qué NO hace |
|---|---|---|
| **{{LIDER}}** (líder) | Decide. Lleva archivos entre el Project, el repo y el dispositivo. Teclea "ejecuta T-NNN". Hace merge y push de `main`. Crea las banderas. Corre lo que pide `sudo`. | No describe el estado del repo de memoria: pide medirlo. |
| **Project claude.ai** "{{PROJECT_CLAUDE}}" (coordinación y diseño) | Diseña, redacta tareas y ADR, revisa cierres, mantiene `BITACORA.md`, las sesiones y `CLAUDE.md`. Propone y prepara el cierre de cada sesión. | No toca el repo ni ve la sesión de Code. No planea sobre un Knowledge desfasado. |
| **Claude Code** (programador, en {{DISPOSITIVO}}) | Ejecuta una tarea: mide (FASE 0), programa en `feature/T-NNN`, verifica, escribe el cierre, pushea la rama. | No decide arquitectura, no escribe ADR, no fusiona, no toca datos reales sin tarea, no toca `.claude/`. |
| **{{REVISOR}}** (revisor) | Lee el repo, usa la web de prueba, comenta. | No opera Claude Code. Sus comentarios pasan por {{LIDER}}. |
| **GitHub** `{{CUENTA_GITHUB}}/{{REPO}}` | Fuente de verdad de código y documentos. | — |

## 2. El ciclo (una tarea = un ciclo)
```
1. Tema en el Project     → el Project escribe docs/tareas/T-NNN_tema.md (completa, con FASE 0)
2. {{LIDER}} la guarda    → scp al worktree de main · git add · commit · push
3. {{LIDER}} en Code      → "ejecuta T-NNN"
4. Code: FASE 0 (mide)    → desviación: STOP y pregunta · sin desviación: trabaja en feature/T-NNN
5. Code: cierre           → docs/cierres/T-NNN_fecha.md, fila de "Estado de trabajos", push de la rama. ESPERA.
6. {{LIDER}} → Project    → chat nuevo: "revisa el cierre de T-NNN" (pega el cierre: vive en la rama)
7. Project                → "listo para merge" / "desviación N: decide X" / "necesita dogrywka"
8. {{LIDER}} prueba       → en la web de prueba, antes del merge
9. {{LIDER}} fusiona      → desde ~/{{RUTA}}_main (ver §5)
```
- **Una tarea viva a la vez.** La siguiente se redacta cuando la anterior cierra: su contenido
  depende del cierre.
- **Tareas pequeñas:** una cosa por tarea, para que el cierre se revise en un turno. Una tarea que
  crece se parte en vueltas (`T-NNN_vuelta2.md`).
- **Tareas escritas para Sonnet** (Code no corre en Opus): pasos explícitos, conteos esperados,
  puntos de paro, banderas previstas y pasos del líder marcados. Plantilla: `docs/plantillas/tarea.md`.
- **Prueba antes del merge:** las correcciones se hacen en la rama, no en `main`.

## 3. Palabras clave (lo que se teclea en Claude Code)
| Escribes | Code hace |
|---|---|
| `ejecuta T-NNN` | Lee la tarea, FASE 0, trabaja, cierra, espera |
| `reconocimiento` | Solo FASE 0 general, sin tarea: para saber dónde estamos |
| `estado` | Resume "Estado de trabajos" de `CLAUDE.md` + `git status` |
| `sí` (a una pregunta destructiva) | Nada por sí solo: la autorización real es la bandera |

## 4. Banderas
`DESTRUCTIVO_OK`, `MERGE_OK` y `ADR_OK` son archivos vacíos en `.claude/` que **solo el líder crea**,
desde su terminal: `touch ~/{{RUTA}}/.claude/DESTRUCTIVO_OK`. El guardián las borra al autorizar
(un solo uso) y le impide a Code crearlas, borrarlas o tocar `.claude/`.
- Regla de rutina sin consultar al Project: comando contra la base de test o una base temporal de la
  sesión → se autoriza; comando que nombra una base con datos reales → se niega.
- Nunca "Always allow" sobre una bandera.
- Después de cada uso, el líder confirma con `ls ~/{{RUTA}}/.claude/` que se consumió. Si se deja una
  armada a propósito, se avisa al Project. Lo que el guardián no trata como destructivo (en Trama,
  `DROP ROLE`) no consume la bandera: se quita a mano con `rm`.

## 5. Merge y push de `main`
`main` está abierto en el worktree `~/{{RUTA}}_main`; el árbol de Code (`~/{{RUTA}}`) trabaja en
ramas `feature/`. Git no deja abrir la misma rama en dos árboles, así que el merge lo hace el líder ahí:
```bash
cd ~/{{RUTA}}_main
git pull
git log --oneline origin/feature/T-NNN..origin/main   # solo debe haber commits de documentos del Project
git merge --no-ff origin/feature/T-NNN -m "Merge T-NNN: <tema>"
git push origin main
git log --oneline -1
```
Si `origin/feature/T-NNN..origin/main` muestra algo que no sean documentos del Project
(`docs/BITACORA.md`, `docs/bitacora/`, `docs/tareas/`, `docs/adr/`), se pregunta al Project antes de
fusionar: la puerta que Code corrió en la rama no cubre ese código. Tras el merge, el líder reinicia lo
que corra desde el árbol (servicio web) y mueve la tarea a `docs/tareas/hechas/` en el siguiente
commit de documentos.

## 6. Guardián
Hook `PreToolUse` de Claude Code (`~/.{{SLUG}}/guardian/guardian.py`), instalado por el líder fuera
del repo para que no cambie con la rama. Falla cerrado: lo que no puede interpretar, lo bloquea.
Bloquea: `git add -A/./--all`; datos y secretos a git; push que no sea `feature/T-NNN` escrito solo;
editar ADR existentes (`ADR_OK`) y cierres existentes (`MERGE_OK`); editar la BITACORA, las sesiones y
los documentos maestros; `DROP`, downgrade y borrados masivos sin `DESTRUCTIVO_OK`; tocar `.claude/`
o `~/.{{SLUG}}/`; `eval`; programas desconocidos dentro de `$(…)` o `bash -c`.
- **Congelado:** un cambio al guardián es una tarea propia con sus pruebas (`make test-guardian`), no
  un arreglo de paso. Los huecos se cierran en el Makefile, en los permisos de la base y en las reglas.
- **Falsos positivos:** Code los reporta sin rodearlos y el líder hace el paso desde su terminal.
  Resueltos en el kit: `git add` de cualquier `.env*.example`, escribir el plan en `~/.claude/plans/`.
  Por diseño: `psql -f` de un archivo que solo existe dentro de un contenedor.
- **Fuera del dispositivo** (una copia del repo clonada por el Project o una sesión de Code en la
  nube) el hook apunta a una ruta que no existe y bloquea toda escritura. Es correcto: ahí no se
  trabaja. El Project que clona el repo trabaja sobre copias fuera del clon.

## 7. Bases de datos (principios; el detalle lo fija el ADR de bases del proyecto)
Lecciones de Trama que aquí son requisito desde el día 1, no consecuencia de un incidente:
1. **Bases por papel:** producción (datos reales), prueba (copia restaurada para el humo y el revisor,
   con su propia web), test (la suite) y, si hace falta, archivo (solo lectura). La guarda es por
   **operación** (`migrar`, `cargar`, `leer`, `aplicacion`…), no por nombre de base.
2. **Rol de la aplicación sin superusuario**, sin `DELETE` sobre tablas de diario y sin acceso a lo que
   no le toca. Contraseñas solo letras y números (van dentro de una URL), puestas por el líder.
3. **La suite solo corre con `make test`**; una guarda sale sin abrir conexión si la base no es la de test.
4. **Postgres registra toda escritura** (`log_statement=mod`, con base y usuario en el prefijo): así se
   mide "0 escrituras de la sesión" en vez de suponerlo.
5. **Respaldo dos veces al día, verificado, con copia fuera del equipo** antes del primer dato real.
   Y una **restauración de prueba programada** (p. ej. semanal): el último respaldo se restaura en una
   base temporal, se comparan conteos de filas contra la original y la temporal se borra. Un respaldo
   que nunca se restauró no está probado (Trama solo validaba el índice del dump y nunca lo agendó).
6. **Todo target que escribe imprime la base** antes de actuar; `include .env` del Makefile pisa
   variables exportadas en la shell (incidente de Trama).

## 8. Documentos y nombres
- **ADR**: `docs/adr/ADR-NNN-titulo-corto.md`, plantilla `docs/plantillas/adr.md`. Solo para decisiones
  de verdad: lo que cambia el modelo, una regla de negocio, la seguridad o la forma de trabajar. Un error
  de captura o de transcripción no lleva ADR. **No se reservan números**: el siguiente número es el
  siguiente ADR redactado. El índice lleva **estado** (propuesto / aceptado / sustituido) y **vigencia**
  (vigente / histórico).
- **Maestros** (modelo de datos, reglas de negocio, reglas de arquitectura): versionados
  `NOMBRE_vX_Y.md`; una versión nueva incorpora los ADR aceptados desde la anterior y deja fuera los
  históricos.
- **Prefijo `AAMMDD_`** solo para artefactos (Excel, dumps, reportes, sesiones de la bitácora); nunca
  para código, carpetas, tablas ni identificadores. Versiones de artefactos `_vX_Y`.
- **Datos**: todo archivo de datos se registra en `docs/datos/REGISTRO_DATOS.md` con SHA-256 y estado.

## 9. BITACORA y sesiones
- `docs/BITACORA.md`: el único documento de estado que se reescribe. Solo lo vigente y lo pendiente.
  **Tope: 30 KB.** En cada cierre lo resuelto sale: a la sesión fechada (lo que pasó) o a un ADR o a una
  línea de "Decisiones vigentes" (lo que se decidió para siempre). En Trama llegó a 207 KB y se leía
  entera en cada sesión.
- `docs/bitacora/AAMMDD_sesion.md`: una por sesión del Project, **write-once**
  (`docs/plantillas/sesion.md`). Segunda sesión del mismo día: `AAMMDD_2_sesion.md`. Es la historia;
  no se reescribe ni se resume después.
- La BITACORA nombra en su encabezado la última sesión; el inicio de sesión del Project compara las dos.
- Ningún entregable importante sale con `[?]` o preguntas abiertas: el Project pide antes el dato.

## 10. Knowledge del Project (fuente de GitHub; la fuente de verdad es git)
- **Una sola fuente:** la sincronización de GitHub del Project, rama `main`, con `CLAUDE.md` y `docs/`
  seleccionados. Nada de código ni datos. Lo nuevo dentro de `docs/` (sesiones, ADR, tareas, cierres
  fusionados) entra solo al sincronizar.
- **No se actualiza sola.** Solo con «Sync now». Es el **último paso de cada cierre**, después del push
  de `main`, y el Project termina cada cierre recordándolo. (Trama: la copia estuvo 13 días atrasada
  sin que nadie lo notara.)
- **Nada subido a mano** de lo que está en git: con dos copias del mismo archivo, la búsqueda del
  Project mezcla versiones. Sueltos solo quedan archivos que no viven en git (p. ej. un Excel).
  Si un proyecto decide que su Project escriba la BITACORA directo en el Knowledge, lo anota como
  decisión vigente con la regla de cuál copia rige.
- **Al iniciar sesión** el Project compara la BITACORA del Knowledge con el último cierre que menciona
  el líder (fecha y hash). Si es más vieja, o hay dos BITACORA, se detiene y pide «Sync now».
- **Lo que vive en una rama** (cierre de Code antes del merge) no está en `main`: se trae pegado.
- **Plan B:** si la sincronización desaparece (Trama, 06-10), se quita la fuente y se suben los
  archivos a mano. Nunca las dos cosas a la vez.
- Si el Knowledge no basta, el Project puede clonar el repo en solo lectura (ver §6, fuera del dispositivo).

## 11. Cierre de sesión del Project
Lista de pasos y comandos: `docs/CIERRE_SESION.md`. En corto: el Project entrega archivos completos
(nunca "pega esto en la sección X"), nunca reconstruye la BITACORA de memoria, lista todo archivo tocado
en el `scp`, recuerda cerrar las sesiones de Code de este proyecto, y el último paso es «Sync now».

## 12. Glosario
**Tarea**: instrucción para Code con FASE 0, fases, puertas y cierre. **Cierre**: reporte write-once de
Code; único canal hacia el Project. **FASE 0 / reconocimiento**: medir antes de tocar. **Desviación
(O-1)**: diferencia entre lo esperado y lo encontrado; se reporta. **Candidato a ADR**: decisión tomada
al implementar que todavía no es ley. **Dogrywka**: archivo adicional a un cierre ya escrito.
**Parcial**: nota de pausa de una tarea partida en sesiones. **Puerta**: condición numérica para
aceptar una tarea. **Humo**: prueba de punta a punta por la web de prueba. **Bandera**: archivo de un
solo uso que autoriza un paso destructivo.
