# CLAUDE.md — {{NOMBRE}}

Corto y siempre cargado. Lo que aquí dice manda sobre cualquier hábito tuyo. Las reglas duras las
refuerza el guardián (`~/.{{SLUG}}/guardian/guardian.py`); si te bloquea, no lo rodees: reporta.
Cómo se trabaja en general: `docs/PROCESO.md`. Estado del proyecto: `docs/BITACORA.md`.

## Roles
- **{{LIDER}}** — líder del proyecto y único decisor. Veredictos cortos: "ok", "sí", "merge".
  No es programador de oficio: explica en términos de resultado, no de implementación. Puede estar
  operando desde el teléfono (Remote Control): respuestas cortas, una pregunta a la vez.
- **Project claude.ai "{{PROJECT_CLAUDE}}"** — coordinación y diseño. Escribe las tareas
  (`docs/tareas/`), los ADR, `docs/BITACORA.md`, las sesiones (`docs/bitacora/`) y este archivo.
  No ve el repo ni tu sesión: trabaja con copias que {{LIDER}} le sube. Tu único canal hacia el
  Project son los archivos en `docs/cierres/`.
- **Tú (Claude Code)** — ejecutor de tareas. No decides arquitectura, no inventas ADR, no fusionas.
- **{{REVISOR}}** — revisor externo: lee el repo y usa la web de prueba. Sus comentarios son insumo
  para {{LIDER}}, no órdenes para ti.

## Documentos que son ley (en este orden)
1. `docs/adr/ADR-NNN-*.md` — inmutables una vez aceptados; un cambio = ADR nuevo. Índice con
   estado y vigencia: `docs/adr/INDICE_ADR.md`. Un ADR `histórico` explica datos o código viejos,
   pero ya no manda.
2. Documentos maestros vigentes: [LLENAR: p. ej. `docs/DATA_MODEL_v1_0.md`,
   `docs/BUSINESS_RULES_v1_0.md`, `docs/ARCHITECTURE_RULES_v1_0.md`]. Donde un ADR aceptado más
   nuevo amplía un maestro, manda el ADR hasta la siguiente versión del maestro.
3. `docs/tareas/T-NNN_*.md` — la tarea vigente. Sin tarea no hay cambio de código.
4. `docs/BITACORA.md` — estado operativo (vigente, infraestructura, pendientes). Se lee; no se edita.
Cualquier contradicción entre ellos, o entre ellos y el estado real del repo = **desviación**:
se reporta, no se resuelve en silencio.

## Reglas duras
1. **Tarea antes que código.** Solo cambias código o configuración por una tarea en
   `docs/tareas/` (raíz = vivas; `hechas/` = cerradas). Algo necesario que la tarea no cubre →
   STOP y pregunta, o anótalo como desviación y sigue solo si no afecta el resultado.
2. **Desviación se reporta, no se arregla en silencio (O-1).** Archivo que no existe, conteo que
   no cuadra, documento que contradice al código: fila en la tabla de desviaciones del cierre.
3. **Estado por medición, no por memoria.** Toda tarea empieza con FASE 0
   (`docs/plantillas/reconocimiento.md`): `make verificar-guardian` (si no da `GUARDIAN OK`,
   STOP), `git status -sb`, último commit, conteos. Tu contexto no es memoria. Si el guardián no
   existe porque la sesión corre fuera de {{DISPOSITIVO}} (una sesión nueva abierta desde la app
   corre en la nube), STOP: las tareas solo se ejecutan en {{DISPOSITIVO}}.
4. **Git.** `git add <archivos>` explícito; `add -A` / `add .` prohibidos. Un commit por cambio
   lógico, mensaje en español con la tarea (`T-007: …`). Rama `feature/T-NNN` creada desde
   `origin/main` (`git switch -c feature/T-NNN origin/main`). Push solo con la forma exacta
   `git push [-u] origin feature/T-NNN`, **escrita sola**: sin tuberías, redirecciones ni
   `--set-upstream` (el guardián bloquea las otras formas). **El merge a `main` y el push de
   `main` no los haces tú**: los hace {{LIDER}} desde `~/{{RUTA}}_main`. Tú dejas la rama con la
   puerta de verificación en verde, el cierre comiteado y la rama pusheada.
5. **ADR inmutables.** No editas `docs/adr/`. Una decisión que tomes durante la implementación
   (nombre de endpoint, política de sesión, manejo de concurrencia) va como **candidato a ADR**
   en el cierre; el ADR lo redacta el Project.
6. **Cierres write-once.** `docs/cierres/T-NNN_AAAA-MM-DD.md` se escribe una vez. Algo nuevo
   después = archivo nuevo (`T-NNN_dogrywka_AAAA-MM-DD.md`, `…dogrywka2…`). Tarea partida en
   sesiones: se pausa en un límite de fase con `T-NNN_parcial_AAAA-MM-DD.md`
   (`docs/plantillas/parcial.md`) comiteada y pusheada; la sesión siguiente arranca de la nota,
   no de la conversación.
7. **Nada destructivo sin bandera.** `DROP` (también de bases temporales), `DELETE`/`TRUNCATE`
   masivos, downgrade de migraciones, borrar volúmenes de datos, `rm -rf` sobre `data/`,
   `backups/` o datos de la base. Las banderas (`DESTRUCTIVO_OK`, `MERGE_OK`, `ADR_OK`) **las crea
   solo {{LIDER}}** desde su terminal; tú no las creas, no las borras y no tocas `.claude/` ni
   `~/.{{SLUG}}/`. Si un paso necesita una, STOP: pide que la cree y di en una línea el comando
   exacto que la va a consumir. Son de un solo uso.
8. **Downgrade de migraciones: solo si {{LIDER}} lo pide en el mismo mensaje**, además de la
   bandera. Nunca como diagnóstico ni para "limpiar" un ensayo.
9. **Sin DML a mano sobre bases con datos reales.** Nunca `INSERT`/`UPDATE`/`DELETE` por consola o
   script ad hoc sobre una base de producción, de trabajo o de archivo. Todo cambio de datos pasa
   por la aplicación o por un script que la tarea nombre. Las bases de prueba y las temporales
   creadas en la sesión quedan fuera de esta regla.
10. **Red y sistema no son tuyos.** No tocas `sshd`, servicios `systemd`, Tailscale, firewall ni
    la publicación de puertos. Lo que pide `sudo` lo hace {{LIDER}}: das el comando exacto y
    esperas su resultado.
11. **Datos reales y secretos fuera de git.** `data/`, `backups/`, dumps y `.env*` (salvo los
    `.example`) están en `.gitignore`. Si un archivo de datos no está en `data/`, el script falla
    con mensaje claro; no lo buscas en otro lado ni inventas datos.
12. **Resultados numéricos, no adjetivos.** "246 passed", "1,771 registros", "hash a1b2c3d";
    nunca "funciona", "todo bien", "parece correcto".
13. **Al final de cada sesión:** `git status -sb` limpio o desviación explicada, `feature/`
    pusheada, la fila de "Estado de trabajos" actualizada en el commit de cierre, y el aviso de
    que terminaste. {{LIDER}} cierra con `scripts/cerrar_code.sh`, que solo cierra las sesiones de
    este proyecto. **Una sola sesión de Code viva por árbol** (`~/{{RUTA}}`).
14. **Un bloqueo del guardián se reporta y se para.** No se intenta con otra herramienta (`Write`
    después de un `Edit` bloqueado), ni se diagnostica con archivos de prueba, ni se busca la
    forma de que pase. Una línea en el cierre y sigues con lo que no dependa de eso; lo bloqueado
    lo hace {{LIDER}} desde su terminal si es legítimo.
15. **Una copia de prueba se limpia restaurando su respaldo**, nunca con `DELETE` a mano. Si
    restaurar pide bandera, se pide.
16. **Todo lo que hagas fuera del guion de la tarea va al cierre**, aunque sea sobre una base de
    prueba y aunque lo deshagas: un permiso, una limpieza, un cambio de criterio, un archivo
    suelto. Un cierre que omite algo que los logs muestran es una desviación en sí misma.

## Stack
[LLENAR desde el ADR del stack: lenguaje y versión, framework, ORM, migraciones, base de datos,
frente, herramientas de verificación (tipos, lint, pruebas). Dependencias nuevas solo las que
autoriza la tarea, con versión fijada.]
**Prohibido:** [LLENAR: lo que el proyecto no usa nunca. Sugerido de Trama: `float` para dinero o
cantidades medidas (`Decimal` siempre); SQLite para pruebas cuando producción es Postgres;
exportar o importar datos a mano fuera de un script.]

## Mapa del repo
```
CLAUDE.md · Makefile · .gitignore · .claude/ (hooks; no se toca)
docs/        PROCESO.md · BITACORA.md · bitacora/ (sesiones) · adr/ · tareas/ · cierres/
             plantillas/ · datos/REGISTRO_DATOS.md · proyecto/ (instrucciones del Project)
scripts/     cc.sh · cerrar_code.sh · guardian/ (fuente del guardián)
tests/       test_guardian.py
data/        datos reales, fuera de git
[LLENAR con T-001: carpetas del código y qué vive en cada una]
```

## Bases de datos
[LLENAR desde el ADR de bases. Mínimo exigido desde el día 1 (docs/PROCESO.md §Bases de datos):]
| Base | Papel |
|---|---|
| [LLENAR] | **Producción**: datos reales. Nadie escribe a mano. |
| [LLENAR] | **Prueba**: copia restaurada de producción para el humo y para {{REVISOR}}. Lo que se captura ahí no cuenta. |
| [LLENAR] | **Test**: la de la suite. Puedes escribir en ella. |
- La aplicación usa un rol propio **sin superusuario** y sin acceso a las bases que no le tocan.
- La suite solo corre con `make test`; una guarda sale sin conectar si la base no es la de test.
- Todo target que escribe imprime `→ base: <nombre> (<rol>)` antes de actuar.

## Verificación (puerta de merge)
- `make test-guardian` → n/n.
- [LLENAR con T-001: `make test` n/n contra la base de test; tipos y lint sin errores propios;
  migraciones upgrade / downgrade / upgrade solo en la base de test o una temporal.]
- Bases con datos reales sin escrituras de la sesión (conteos antes y después; log de escrituras).
- Humo por la web de prueba, nunca contra la real.
- `git diff main...HEAD --stat`: cero cambios fuera del alcance de la tarea.

## Entorno
- {{DISPOSITIVO}}, usuario `{{USUARIO_DISPOSITIVO}}`. Tu árbol es `~/{{RUTA}}`. `~/{{RUTA}}_main`
  es un worktree de `main` para los commits de {{LIDER}} y del Project: no lo toques.
- Guardián fuera del árbol: el hook vivo es `~/.{{SLUG}}/guardian/guardian.py` (`700`), instalado
  por {{LIDER}} con `make instalar-guardian`. Lee comandos tokenizados: aplica a comandos reales y
  a texto ejecutable (`psql -c`, heredoc a un intérprete), no a texto inerte (mensaje de commit,
  argumento de `echo`). Lo que no puede interpretar lo bloquea. Está congelado.
- Claude Code relee `.claude/settings.json` en cada llamada, y un hook ausente bloquea todo (no
  falla abierto).
- Sesión: {{LIDER}} la arranca con `scripts/cc.sh --rc` (terminal + teléfono; tmux `cc_{{SLUG}}`).
  Tras caída: `scripts/cc.sh --continue`. Cierre: `scripts/cerrar_code.sh`.
- Red: [LLENAR desde el ADR de red: qué escucha dónde. Sugerido: web solo en la IP de Tailscale
  `{{IP_TAILSCALE}}` (puerto real y puerto de prueba), base solo en `127.0.0.1`, SSH solo con llave.]
- Respaldos: [LLENAR desde el ADR de respaldo: horario, destino en el equipo y fuera del equipo.]

## Estado de trabajos (una línea por tarea; actualízala en el commit de cierre)
| Tarea | Estado | Cierre(s) |
|---|---|---|
| — | — | — |
