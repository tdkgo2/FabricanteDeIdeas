# Makefile de {{NOMBRE}}
# Parte 1: proceso (viene del kit, no se toca sin tarea).
# Parte 2: stack (la agrega T-001 según el ADR del stack). Reglas que debe cumplir en
#          docs/PROCESO.md §Bases de datos: pruebas solo con `make test` y guarda, operaciones
#          destructivas con bandera, cada target que escribe imprime la base antes de actuar.

SHELL := /bin/bash
GUARDIAN_DEST ?= $(HOME)/.{{SLUG}}/guardian
# Python de las pruebas del guardián: el del venv del proyecto (ruta absoluta: cron corre con
# un PATH mínimo). Si todavía no hay venv: python3 -m venv .venv && .venv/bin/pip install pytest
PY ?= $(CURDIR)/.venv/bin/python

.DEFAULT_GOAL := ayuda
.PHONY: ayuda estado instalar-guardian verificar-guardian test-guardian cerrar-code

ayuda:               ## lista los objetivos
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | expand -t 22

estado:              ## solo lectura: rama, últimos commits, tareas vivas, últimos cierres
	@git status -sb
	@git log --oneline -5
	@echo "Tareas vivas:"; ls docs/tareas/*.md 2>/dev/null || echo "  ninguna"
	@echo "Últimos cierres:"; ls -t docs/cierres/*.md 2>/dev/null | head -5 | grep . || echo "  ninguno"

instalar-guardian:   ## lo corre SOLO el líder: instala el guardián vivo fuera del repo, 700
	mkdir -p $(GUARDIAN_DEST)
	chmod 700 $(GUARDIAN_DEST)
	cp scripts/guardian/guardian.py $(GUARDIAN_DEST)/guardian.py
	chmod 700 $(GUARDIAN_DEST)/guardian.py
	chmod 700 .claude
	@sha256sum $(GUARDIAN_DEST)/guardian.py

verificar-guardian:  ## solo lectura: hash instalado vs fuente, settings.json, permisos de .claude/
	@ok=1; \
	origen=$$(sha256sum scripts/guardian/guardian.py | awk '{print $$1}'); \
	instalado=$$(sha256sum $(GUARDIAN_DEST)/guardian.py 2>/dev/null | awk '{print $$1}'); \
	if [ -z "$$instalado" ]; then echo "FALTA: $(GUARDIAN_DEST)/guardian.py no existe"; ok=0; \
	elif [ "$$origen" != "$$instalado" ]; then echo "DESINCRONIZADO: $(GUARDIAN_DEST)/guardian.py no coincide con scripts/guardian/guardian.py"; ok=0; \
	fi; \
	if ! grep -q "$(GUARDIAN_DEST)/guardian.py" .claude/settings.json 2>/dev/null; then \
		echo "settings.json no apunta a $(GUARDIAN_DEST)/guardian.py"; ok=0; \
	fi; \
	permisos=$$(stat -c '%a' .claude 2>/dev/null); \
	if [ "$$permisos" != "700" ]; then echo ".claude/ no está en 700 (está en $$permisos)"; ok=0; fi; \
	if [ "$$ok" = "1" ]; then echo "GUARDIAN OK"; else exit 1; fi

test-guardian:       ## pruebas del guardián en un sandbox temporal (nunca contra el instalado)
	$(PY) -m pytest -q -p no:cacheprovider tests/test_guardian.py

cerrar-code:         ## cierra las sesiones de Claude Code de ESTE proyecto (no las de otros)
	@bash scripts/cerrar_code.sh

# ---------------------------------------------------------------------------------------------
# Parte 2 — stack. La agrega T-001. Mínimo exigido (docs/PROCESO.md §Bases de datos):
#   test       pytest SOLO contra la base de pruebas; la guarda sale sin conectar si no lo es
#   backup     respaldo de las bases con datos reales, verificado, con copia fuera del equipo
#   migrate    respalda antes si la base es de producción
#   downgrade  exige y consume DESTRUCTIVO_OK; se niega sobre bases con datos reales
#   web-prueba levanta la web de prueba contra la base de prueba (para el revisor y el humo)
# ---------------------------------------------------------------------------------------------
