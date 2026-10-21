#!/usr/bin/env bash
# Cierra las sesiones de Claude Code de {{NOMBRE}} y SOLO las de este proyecto.
#
# Por qué existe: Remote Control no tiene /exit en modo servidor y deja viva cada sesión que
# abre (en Trama llegaron a ser ocho). El remedio de Trama, `pkill -f -- '--sdk-url'`, mata las
# sesiones de TODOS los proyectos del dispositivo. Aquí se elige por carpeta de trabajo: un
# proceso de Claude Code cuyo directorio actual está dentro de este árbol.
#
# Uso:  scripts/cerrar_code.sh           # cierra y muestra lo que queda
#       scripts/cerrar_code.sh --ver     # solo muestra, no cierra nada
set -u
DIR_REAL=$(readlink -f "$HOME/{{RUTA}}")
SESION="cc_{{SLUG}}"
SOLO_VER=0
[ "${1:-}" = "--ver" ] && SOLO_VER=1
# Dentro de Claude Code (CLAUDECODE=1) solo se permite mirar: cerrar mataría la propia sesión.
if [ "${CLAUDECODE:-}" = "1" ] && [ "$SOLO_VER" -eq 0 ]; then
  echo "cerrar_code.sh lo corre el líder desde su terminal. Dentro de Code: scripts/cerrar_code.sh --ver" >&2
  exit 1
fi

propios=()
for pid in $(pgrep -f -- '(^|[ /])claude( |$)|claude-code|--sdk-url|remote-control' 2>/dev/null); do
  [ "$pid" = "$$" ] && continue
  # El servidor de tmux es uno solo para todo el dispositivo: matarlo cerraría también las
  # sesiones de los otros proyectos. La sesión propia se cierra con kill-session, más abajo.
  case "$(ps -o comm= -p "$pid" 2>/dev/null)" in tmux*) continue ;; esac
  cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null) || continue
  case "$cwd" in
    "$DIR_REAL"|"$DIR_REAL"/*) propios+=("$pid") ;;
  esac
done

echo "Proyecto: $DIR_REAL"
if [ "${#propios[@]}" -eq 0 ]; then
  echo "Procesos de Claude Code de este proyecto: 0"
else
  echo "Procesos de Claude Code de este proyecto: ${#propios[@]}"
  ps -o pid=,args= -p "$(IFS=,; echo "${propios[*]}")"
fi

if [ "$SOLO_VER" -eq 0 ]; then
  if tmux has-session -t "$SESION" 2>/dev/null; then
    tmux kill-session -t "$SESION" && echo "tmux $SESION: cerrada"
  else
    echo "tmux $SESION: no estaba abierta"
  fi
  if [ "${#propios[@]}" -gt 0 ]; then
    kill "${propios[@]}" 2>/dev/null
    sleep 2
    for pid in "${propios[@]}"; do
      kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null
    done
    echo "Cerrados: ${#propios[@]}"
  fi
fi

echo
echo "Sesiones de Claude Code que quedan en el dispositivo (de cualquier proyecto):"
# El servidor de tmux guarda en su línea de comando la orden con que nació (p. ej. la de cc_telas)
# aunque esa sesión ya no exista: no es una sesión de Code y no se lista.
ps -ef | grep -E -- '--sdk-url|remote-control' | grep -v -E 'grep|tmux (new-session|new|attach)' || echo "  ninguna"
echo "tmux:"
tmux ls 2>/dev/null || echo "  sin sesiones"
