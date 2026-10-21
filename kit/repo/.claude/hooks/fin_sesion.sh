#!/usr/bin/env bash
# Hook Stop: recordatorio no bloqueante si el árbol de trabajo no está limpio o hay banderas activas.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
n=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$n" -gt 0 ]; then
  echo "FIN DE SESIÓN: $n archivos sin commitear. Antes de /clear: git add <archivos> + commit, o explica en el cierre por qué quedan." >&2
fi
for f in .claude/MERGE_OK .claude/DESTRUCTIVO_OK .claude/ADR_OK; do
  [ -f "$f" ] && echo "FIN DE SESIÓN: la bandera $f sigue activa. Avísale al líder: la quita él (tú no tocas .claude/)." >&2
done
exit 0
