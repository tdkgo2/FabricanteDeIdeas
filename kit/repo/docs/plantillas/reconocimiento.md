# FASE 0 — Reconocimiento (medir, no cambiar)

El estado se establece por medición, nunca por memoria de sesión ni por lo que diga un documento.
Cero ediciones, cero `git checkout` que cambie el árbol, **la suite no se corre aquí** (en Trama, un
`pytest` de reconocimiento escribió en producción).

| # | Qué | Comando |
|---|---|---|
| 1 | Guardián instalado y sincronizado | `make verificar-guardian` — **STOP si no imprime `GUARDIAN OK`** |
| 2 | Rama, limpieza, relación con origin | `git status -sb` |
| 3 | Últimos commits de main | `git fetch origin && git log --oneline -5 origin/main` |
| 4 | Ramas feature sin fusionar | `git branch -r --no-merged origin/main` |
| 5 | Tareas vivas | `ls docs/tareas/*.md` |
| 6 | Últimos cierres | `ls -t docs/cierres | head -5` |
| 7 | "Estado de trabajos" | `grep -A30 'Estado de trabajos' CLAUDE.md` |
| 8 | Banderas presentes | `ls .claude/` (solo leer; si hay una `*_OK`, se reporta) |
| 9 | Sesiones de Code vivas de este proyecto | `scripts/cerrar_code.sh --ver` |
| 10 | Mediciones del stack | [LLENAR con T-001: servicios arriba, migración actual, conteos por base] |
| 11 | Datos de la tarea | `sha256sum data/<archivo>` contra `docs/datos/REGISTRO_DATOS.md` |
| 12 | Mediciones propias de la tarea | según la tabla FASE 0 de la tarea |

## Resultado
Tabla `| # | Medición | Resultado | ¿Coincide con lo esperado por la tarea? |`.
Cada fila que no coincide → fila en "Desviaciones" + **STOP antes de FASE 1**; esperas el veredicto
de {{LIDER}}. Sin desviaciones → FASE 1 sin preguntar.
