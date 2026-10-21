#!/usr/bin/env bash
# Crea el repo de un proyecto nuevo a partir del kit.
#
# Uso:  bash instanciar.sh valores.env [destino]
#   valores.env  copia llena de valores.ejemplo.env (vive fuera de cualquier repo: ~/valores_<slug>.env)
#   destino      carpeta nueva (por omisión: $HOME/<RUTA>); debe no existir o estar vacía
#
# Qué hace: copia repo/ al destino, sustituye los {{MARCADORES}} en contenido y nombres de archivo
# (más FECHA y AAMMDD de hoy), y se niega a terminar si queda alguno. Junto al destino crea
# <destino>_arranque/ con lo que va al Project de claude.ai y no al repo: instrucciones.txt,
# descripcion.txt y traspaso.txt. No toca git, ni red, ni nada fuera de esas dos carpetas.
# Las secciones [LLENAR …] quedan para el Project (primeros ADR).
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)"
VALORES="${1:-}"
if [ -z "$VALORES" ] || [ ! -f "$VALORES" ]; then
  echo "uso: bash instanciar.sh valores.env [destino]" >&2
  exit 1
fi

python3 - "$KIT" "$VALORES" "${2:-}" <<'PY'
import datetime
import os
import re
import shutil
import sys
from pathlib import Path

kit, archivo_valores, destino_arg = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
REQUERIDAS = [
    "NOMBRE", "SLUG", "DESCRIPCION_CORTA", "REPO", "CUENTA_GITHUB", "PROJECT_CLAUDE", "RUTA",
    "LIDER", "REVISOR", "DISPOSITIVO", "USUARIO_DISPOSITIVO", "IP_LAN", "IP_TAILSCALE", "DESCARGAS",
]

valores: dict[str, str] = {}
for n, linea in enumerate(archivo_valores.read_text(encoding="utf-8").splitlines(), 1):
    linea = linea.strip()
    if not linea or linea.startswith("#"):
        continue
    if "=" not in linea:
        sys.exit(f"{archivo_valores}:{n}: falta '=' en «{linea}»")
    clave, valor = linea.split("=", 1)
    valores[clave.strip()] = valor.strip()

faltan = [k for k in REQUERIDAS if not valores.get(k)]
if faltan:
    sys.exit("Faltan valores: " + ", ".join(faltan))
if not re.fullmatch(r"[a-z][a-z0-9_]*", valores["SLUG"]):
    sys.exit("SLUG: solo minúsculas, números y guion bajo, empezando con letra")
if valores["RUTA"].startswith(("/", "~")) or ".." in valores["RUTA"]:
    sys.exit("RUTA va relativa a HOME, sin '/' ni '~' al inicio (p. ej. Proyectos/Jornada)")
if " " in valores["DESCARGAS"]:
    sys.exit("DESCARGAS sin espacios (va en comandos de PowerShell sin comillas)")

hoy = datetime.date.today()
valores["FECHA"] = hoy.isoformat()
valores["AAMMDD"] = hoy.strftime("%y%m%d")

destino = Path(destino_arg) if destino_arg else Path.home() / valores["RUTA"]
destino = destino.expanduser().resolve()
arranque = destino.with_name(destino.name + "_arranque")
for carpeta in (destino, arranque):
    if carpeta.exists() and any(carpeta.iterdir()):
        sys.exit(f"{carpeta} ya existe y no está vacía: no se sobrescribe nada")

origen = kit / "repo"
shutil.copytree(origen, destino, dirs_exist_ok=True)

MARCA = re.compile(r"\{\{([A-Z_]+)\}\}")


def sustituir(texto: str) -> str:
    return MARCA.sub(lambda m: valores.get(m.group(1), m.group(0)), texto)


def sin_nota(texto: str) -> str:
    """Quita la nota '> …' que sigue al título: es para quien lee el repo, no se pega."""
    lineas = texto.splitlines()
    nota = [i for i, l in enumerate(lineas[:12]) if l.startswith(">")]
    if nota:
        ini, fin = nota[0], nota[-1] + 1
        if fin < len(lineas) and not lineas[fin].strip():
            fin += 1  # la línea en blanco que sigue a la nota también sale
        del lineas[ini:fin]
    return "\n".join(lineas) + "\n"


cambiados = 0
for ruta in sorted(destino.rglob("*"), key=lambda p: len(p.parts), reverse=True):
    if ruta.is_file():
        try:
            texto = ruta.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        nuevo = sustituir(texto)
        if nuevo != texto:
            ruta.write_text(nuevo, encoding="utf-8")
            cambiados += 1
    nombre_nuevo = sustituir(ruta.name)
    if nombre_nuevo != ruta.name:
        ruta.rename(ruta.with_name(nombre_nuevo))

# Lo que va al Project de claude.ai y no al repo. Se escribe con CRLF para el Bloc de notas.
arranque.mkdir(parents=True, exist_ok=True)
proyecto = destino / "docs" / "proyecto"
para_project = {
    "instrucciones.txt": sin_nota((proyecto / "INSTRUCCIONES_PROJECT.md").read_text(encoding="utf-8")),
    "descripcion.txt": sin_nota((proyecto / "DESCRIPCION_PROJECT.md").read_text(encoding="utf-8")),
    "traspaso.txt": sustituir((kit / "arranque" / "traspaso.txt").read_text(encoding="utf-8")),
}
for nombre, texto in para_project.items():
    (arranque / nombre).write_text(texto, encoding="utf-8", newline="\r\n")

restos = []
llenar = 0
for base in (destino, arranque):
    for ruta in base.rglob("*"):
        if ruta.is_file():
            texto = ruta.read_text(encoding="utf-8", errors="replace")
            for m in MARCA.finditer(texto):
                restos.append(f"{ruta.relative_to(base.parent)}: {m.group(0)}")
            if base == destino:
                llenar += texto.count("[LLENAR")
        if MARCA.search(ruta.name):
            restos.append(f"nombre de archivo: {ruta.relative_to(base.parent)}")
if restos:
    print("\n".join(restos))
    sys.exit(f"Quedan {len(restos)} marcadores sin valor. Revisa valores.env.")

for script in ("scripts/cc.sh", "scripts/cerrar_code.sh", ".claude/hooks/fin_sesion.sh"):
    p = destino / script
    p.chmod(p.stat().st_mode | 0o111)

try:
    remoto = "~/" + str(arranque.relative_to(Path.home()))
except ValueError:
    remoto = str(arranque)
print(f"Listo: {destino}")
print(f"  archivos con valores sustituidos: {cambiados}")
print(f"  marcadores sin valor: 0")
print(f"  secciones [LLENAR …] para los primeros ADR: {llenar}")
print(f"Para el Project (paso G): {arranque}")
print(f"  {', '.join(para_project)}")
print(f"  a la laptop: scp -r {valores['USUARIO_DISPOSITIVO']}@{valores['IP_LAN']}:{remoto} {valores['DESCARGAS']}\\")
print("Siguiente: docs/GUIA_DIA_0.md, paso C.")
PY
