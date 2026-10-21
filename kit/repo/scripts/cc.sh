#!/usr/bin/env bash
# Arranca Claude Code de {{NOMBRE}} en el dispositivo, dentro de tmux y con Remote Control:
# la sesión sobrevive si se cae el SSH y se ve desde la app Claude (pestaña Code).
#
# Uso:  scripts/cc.sh --rc        # lo normal: terminal interactiva + teléfono
#       scripts/cc.sh             # modo servidor: solo muestra el QR, no acepta texto
#       scripts/cc.sh --continue  # tras caída del proceso: retoma la sesión
# Cerrar: scripts/cerrar_code.sh (solo cierra las sesiones de ESTE proyecto).
#
# Una sesión nueva abierta desde la app corre en la nube: sin guardián, sin base y sin la red
# del dispositivo. No sirve para tareas (CLAUDE.md regla 3).
# Requisitos: tmux, claude (login con cuenta claude.ai, no clave API).
set -e
DIR="$HOME/{{RUTA}}"
NOMBRE="{{SLUG}}"
SESION="cc_${NOMBRE}"
cd "$DIR"
case "${1:-}" in
  --continue) CMD="claude remote-control --continue" ;;
  --rc)       CMD="claude --remote-control \"$NOMBRE\"" ;;
  *)          CMD="claude remote-control --name \"$NOMBRE\"" ;;
esac
if command -v tmux >/dev/null 2>&1; then
  if tmux has-session -t "$SESION" 2>/dev/null; then exec tmux attach -t "$SESION"; fi
  exec tmux new-session -s "$SESION" -c "$DIR" "$CMD; echo; echo 'claude terminó. Retomar: scripts/cc.sh --continue'; exec bash"
else
  echo "Sin tmux: la sesión NO sobrevive al corte de SSH. Instala: sudo apt install tmux" >&2
  exec bash -c "$CMD"
fi
