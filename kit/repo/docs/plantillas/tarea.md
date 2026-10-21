# T-NNN: <tema>

**Fecha:** AAAA-MM-DD · **Ejecuta:** Claude Code (Sonnet) · **Sesiones previstas:** 1
**Rama:** `feature/T-NNN` desde `origin/main` (`git switch -c feature/T-NNN origin/main`)
**Base:** ADR-xxx · <maestro> vX_Y §n · **Datos:** <archivos de `data/` con su SHA-256 de REGISTRO_DATOS, o "ninguno">
**Banderas previstas:** <ninguna | `DESTRUCTIVO_OK` para <comando exacto>> — las crea {{LIDER}}
**Pasos de {{LIDER}}:** marcados con **[{{LIDER}}]**; Code se detiene, da el comando exacto y espera el resultado.

## Objetivo (una frase, en términos de resultado)

## Por qué (dos o tres líneas; qué problema real resuelve)

## FASE 0 — reconocimiento (sin cambios)
Sigue `docs/plantillas/reconocimiento.md`, más:
| # | Medición | Comando / lugar | Esperado |
|---|---|---|---|
| a | … | … | … |
Desviación → STOP al final de FASE 0, reporta en una tabla, espera veredicto. Sin desviación → FASE 1.

## FASE 1 — <…>
1. …
**Punto de paro:** <qué se muestra a {{LIDER}} antes de seguir, si aplica>

## FASE 2 — <…>

## Humo (contra la web y la base de prueba, nunca la real)
| # | Paso | Resultado esperado |
|---|---|---|

## Puertas de aceptación (números)
- [ ] `make test-guardian` n/n · `make test` n/n
- [ ] <tipos / lint sin errores propios>
- [ ] <conteos esperados>
- [ ] bases con datos reales sin escrituras de la sesión (conteos antes/después y log)
- [ ] cero cambios fuera del alcance (`git diff main...HEAD --stat`)

## Fuera de alcance (explícito)
- …

## Cierre
`docs/cierres/T-NNN_AAAA-MM-DD.md` según `docs/plantillas/cierre.md`; fila de "Estado de trabajos"
en `CLAUDE.md` en el mismo commit; push de `feature/T-NNN` escrito solo. **No hay merge**: lo hace
{{LIDER}} tras la revisión del Project y su prueba. Si la sesión se acaba antes: pausa en un límite
de fase con `docs/plantillas/parcial.md`.
