# Cierre de sesión del Project — {{NOMBRE}}

**Cuándo:** el Project lo propone al llegar a un hito (tarea redactada, cierre revisado, merge) o
cuando la conversación va larga. Con la palabra **"cierre"**, cierra de inmediato.

## 1. Lo que entrega el Project
Archivos **completos**, listos para reemplazar, como descargables. Nunca "pega esto en la sección X".

| Archivo | Cuándo | Destino en el repo |
|---|---|---|
| `AAMMDD_sesion.md` | siempre (nuevo, write-once) | `docs/bitacora/` |
| `BITACORA.md` | siempre | `docs/` |
| `CLAUDE.md` | si cambió | raíz |
| `INDICE_ADR.md` y `ADR-NNN-*.md` nuevos | si hubo ADR | `docs/adr/` |
| `T-NNN_*.md` | si se redactó una tarea | `docs/tareas/` |
| `REGISTRO_DATOS.md` | si se generó un archivo de datos | `docs/datos/` |
| archivos de datos | si se generaron | `data/` (fuera de git) |

**Antes de entregar, el Project comprueba:**
- Trabajó sobre el archivo completo y actual. Si no lo tiene, lo pide; **nunca reconstruye la
  BITACORA de memoria**. Versión real: `cd ~/{{RUTA}}_main && git pull && head -3 docs/BITACORA.md`.
- Ningún `[?]` ni pregunta abierta en lo que entrega.
- La BITACORA cabe en 30 KB; lo resuelto salió a la sesión o a un ADR.
- Todo archivo tocado en la sesión está en la tabla y en los comandos de abajo.

## 2. Pasos de {{LIDER}}

### Paso 1 — Descargar
Todo a `{{DESCARGAS}}`. Si el navegador agrega `(1)` al nombre, renómbralo antes de copiar.

### Paso 2 — Poner `main` al día en el dispositivo (terminal SSH)
```bash
ssh {{USUARIO_DISPOSITIVO}}@{{IP_LAN}}
cd ~/{{RUTA}}_main
git pull
```

### Paso 3 — Copiar los archivos (PowerShell en la laptop, ventana aparte)
Una línea por archivo entregado; el Project las escribe con los nombres reales. Ejemplo:
```powershell
scp {{DESCARGAS}}\BITACORA.md {{USUARIO_DISPOSITIVO}}@{{IP_LAN}}:~/{{RUTA}}_main/docs/BITACORA.md
scp {{DESCARGAS}}\AAMMDD_sesion.md {{USUARIO_DISPOSITIVO}}@{{IP_LAN}}:~/{{RUTA}}_main/docs/bitacora/
```

### Paso 4 — Commit y push de `main` (terminal SSH)
```bash
cd ~/{{RUTA}}_main
git status -sb                      # solo deben aparecer los archivos copiados
git add docs/BITACORA.md docs/bitacora/AAMMDD_sesion.md
git commit -m "Cierre AAAA-MM-DD: <tema>"
git push origin main
git log --oneline -1                # anota el hash: el Project lo pide en la sesión siguiente
```
Si se fusionó una tarea en la sesión: `git mv docs/tareas/T-NNN_*.md docs/tareas/hechas/` en este
mismo commit.

### Paso 5 — Cerrar las sesiones de Code de este proyecto (si hubo tarea)
```bash
~/{{RUTA}}/scripts/cerrar_code.sh
```
Debe terminar con "Procesos de Claude Code de este proyecto" cerrados y mostrar solo sesiones de
otros proyectos, si las hay. No uses `pkill -f -- '--sdk-url'`: cierra las de todos los proyectos.

### Paso 6 — Banderas
```bash
ls ~/{{RUTA}}/.claude/              # no debe haber ningún *_OK
```

### Paso 7 — Knowledge del Project (siempre el último)
- Reemplaza `BITACORA.md`.
- Quita la sesión anterior y sube la nueva (`AAMMDD_sesion.md`).
- Si cambiaron: `CLAUDE.md`, `INDICE_ADR.md`. Sube los ADR nuevos y la tarea nueva.
- Si hubo merge: sube el `CLAUDE.md` de `main` (Code editó su "Estado de trabajos").

La sesión siguiente empieza comprobando que el Knowledge diga lo mismo que este cierre.
