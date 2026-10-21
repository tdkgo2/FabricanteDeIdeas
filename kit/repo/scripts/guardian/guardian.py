#!/usr/bin/env python3
"""Guardián v2 — kit de proyecto (origen: Trama, ADR-047 y T-009 de CdL_Trama).

PreToolUse de Claude Code: lee JSON por stdin; exit 0 = permite, exit 2 = bloquea.
Vive fuera del árbol de trabajo (~/.{{SLUG}}/guardian/); la fuente es este archivo.
Solo biblioteca estándar, compatible con /usr/bin/python3 (3.10+).
Reglas y razones: docs/PROCESO.md §Guardián y CLAUDE.md, reglas duras.
Está congelado: un cambio aquí es una tarea propia, no un arreglo de paso.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROYECTO_SLUG = "{{SLUG}}"
LIDER = "{{LIDER}}"

FLAG_NAMES = ("MERGE_OK", "DESTRUCTIVO_OK", "ADR_OK")

# Programas que el guardián reconoce sin ambigüedad (tienen regla propia o son
# lectura inocua). Dentro de una sustitución ($(...), backticks) o de un
# "bash -c"/"sh -c", un programa que no esté aquí bloquea sin bandera posible:
# ahí el comando no es visible en el comando real, así que no se arriesga.
SAFE_READERS = {"ls", "stat", "cat", "head", "tail", "grep", "sha256sum", "diff", "test", "["}
KNOWN_PROGRAMS = SAFE_READERS | {
    "git", "docker", "docker-compose", "alembic", "rm", "psql", "bash", "sh", "make",
    "python", "python3", "pytest", "mypy", "ruff", "pip", "echo", "printf", "touch",
    "chmod", "mkdir", "wc", "df", "source", "true", "false", "pwd", "cd", "tee",
    "find", "xargs", "sort", "uniq", "sleep", "env", "command", "time", "nohup",
}

SQL_DESTRUCTIVE_RE = re.compile(r"DROP\s+(DATABASE|TABLE|SCHEMA)", re.IGNORECASE)
PROTECTED_RE = re.compile(
    r"(^|/)\.claude(/|$)|(^|/)\." + re.escape(PROYECTO_SLUG) + r"(/|$)"
)
# ~/.claude/plans/ es donde Claude Code guarda el plan en modo plan: no es el .claude/ del
# proyecto ni contiene banderas. Falso positivo de Trama (T-015).
PLANES_PERMITIDOS = ("~/.claude/plans/", str(Path.home() / ".claude" / "plans") + "/")

HEREDOC_RE = re.compile(r"<<(-)?\s*(['\"]?)(\w+)\2")


@dataclass
class Analysis:
    """Resultado de analizar un fragmento de comando."""

    hard_block: str | None = None
    needs: set[str] = field(default_factory=set)

    def merge(self, other: Analysis) -> None:
        if self.hard_block is not None:
            return
        if other.hard_block is not None:
            self.hard_block = other.hard_block
            return
        self.needs |= other.needs


def _collapse_ws(texto: str) -> str:
    return re.sub(r"\s+", " ", texto)


def _is_protected_path(token: str) -> bool:
    if token.startswith(PLANES_PERMITIDOS) and ".." not in token:
        return False
    return bool(PROTECTED_RE.search(token))


def _strip_single_quoted(texto: str) -> list[tuple[int, int]]:
    """Devuelve los rangos [inicio, fin) que están dentro de comillas simples."""
    rangos = []
    in_single = False
    start = 0
    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]
        if c == "'" and not in_single:
            in_single = True
            start = i
        elif c == "'" and in_single:
            in_single = False
            rangos.append((start, i + 1))
        i += 1
    if in_single:
        rangos.append((start, n))
    return rangos


def _dentro_de(rangos: list[tuple[int, int]], pos: int) -> bool:
    return any(a <= pos < b for a, b in rangos)


def extraer_heredocs(texto: str) -> tuple[str, dict[str, str]]:
    """Quita cuerpos de heredoc del texto, los reemplaza por marcadores."""
    cuerpos: dict[str, str] = {}
    contador = 0
    salida = []
    pos = 0
    comillas_simples = _strip_single_quoted(texto)
    while True:
        m = HEREDOC_RE.search(texto, pos)
        if not m:
            salida.append(texto[pos:])
            break
        if _dentro_de(comillas_simples, m.start()):
            # Dentro de comillas simples no hay heredoc real.
            salida.append(texto[pos:m.end()])
            pos = m.end()
            continue
        salida.append(texto[pos:m.start()])
        dash, _q, delim = m.groups()
        fin_linea = texto.find("\n", m.end())
        if fin_linea == -1:
            salida.append(" __HEREDOC_UNCLOSED__ ")
            pos = len(texto)
            break
        inicio_cuerpo = fin_linea + 1
        if dash:
            term_re = re.compile(rf"(?m)^[ \t]*{re.escape(delim)}[ \t]*$")
        else:
            term_re = re.compile(rf"(?m)^{re.escape(delim)}[ \t]*$")
        tm = term_re.search(texto, inicio_cuerpo)
        if not tm:
            salida.append(" __HEREDOC_UNCLOSED__ ")
            pos = len(texto)
            break
        cuerpo = texto[inicio_cuerpo:tm.start()]
        nombre = f"__HEREDOC_{contador}__"
        cuerpos[nombre] = cuerpo
        contador += 1
        salida.append(f" {nombre} ")
        pos = tm.end()
    return "".join(salida), cuerpos


def extraer_sustituciones(texto: str) -> tuple[str, dict[str, str]]:
    """Quita $(...) y `...` del texto, los reemplaza por marcadores."""
    subs: dict[str, str] = {}
    contador = 0
    salida = []
    i = 0
    n = len(texto)
    in_single = False
    while i < n:
        c = texto[i]
        if c == "'" and not in_single:
            in_single = True
            salida.append(c)
            i += 1
            continue
        if c == "'" and in_single:
            in_single = False
            salida.append(c)
            i += 1
            continue
        if in_single:
            salida.append(c)
            i += 1
            continue
        if c == "$" and i + 1 < n and texto[i + 1] == "(":
            depth = 1
            j = i + 2
            while j < n and depth > 0:
                if texto[j] == "(":
                    depth += 1
                elif texto[j] == ")":
                    depth -= 1
                j += 1
            if depth != 0:
                salida.append(" __SUBST_UNCLOSED__ ")
                i = n
                break
            inner = texto[i + 2 : j - 1]
            nombre = f"__SUBST_{contador}__"
            subs[nombre] = inner
            contador += 1
            salida.append(f" {nombre} ")
            i = j
            continue
        if c == "`":
            j = texto.find("`", i + 1)
            if j == -1:
                salida.append(" __SUBST_UNCLOSED__ ")
                i = n
                break
            inner = texto[i + 1 : j]
            nombre = f"__SUBST_{contador}__"
            subs[nombre] = inner
            contador += 1
            salida.append(f" {nombre} ")
            i = j + 1
            continue
        salida.append(c)
        i += 1
    return "".join(salida), subs


def tokenizar(texto: str) -> list[str] | None:
    """Tokeniza con shlex (punctuation_chars=True). None si no se puede."""
    try:
        lexer = shlex.shlex(texto, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        return list(lexer)
    except ValueError:
        return None


SEPARADORES = {"&&", "||", ";", "|"}


def partir_en_comandos_simples(tokens: list[str]) -> list[list[str]]:
    comandos: list[list[str]] = []
    actual: list[str] = []
    for tok in tokens:
        if tok in SEPARADORES:
            comandos.append(actual)
            actual = []
        else:
            actual.append(tok)
    comandos.append(actual)
    return [c for c in comandos if c]


def despojar_envoltorios(argv: list[str]) -> tuple[list[str], dict[str, str]]:
    """Quita sudo/env/VAR=x/time/nohup/command del frente. Devuelve argv y asignaciones."""
    asignaciones: dict[str, str] = {}
    i = 0
    asign_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    while i < len(argv):
        tok = argv[i]
        m = asign_re.match(tok)
        if m:
            asignaciones[m.group(1)] = m.group(2)
            i += 1
            continue
        base = os.path.basename(tok)
        if base in ("sudo", "nohup", "command"):
            i += 1
            continue
        if base == "time":
            i += 1
            continue
        if base == "env":
            i += 1
            # env puede traer sus propias VAR=x antes del comando real
            while i < len(argv) and asign_re.match(argv[i]):
                m2 = asign_re.match(argv[i])
                assert m2 is not None
                asignaciones[m2.group(1)] = m2.group(2)
                i += 1
            continue
        break
    return argv[i:], asignaciones


def resolver_programa(argv: list[str]) -> tuple[str, list[str]]:
    """Resuelve docker exec / docker compose exec hacia el programa real."""
    if not argv:
        return "", []
    base = os.path.basename(argv[0])
    if base == "docker" and len(argv) >= 2:
        if argv[1] == "exec":
            resto = argv[2:]
            j = 0
            while j < len(resto) and resto[j].startswith("-"):
                if resto[j] in ("-u", "--user", "-w", "--workdir"):
                    j += 2
                else:
                    j += 1
            if j < len(resto):
                j += 1  # nombre del contenedor
            if j < len(resto):
                return os.path.basename(resto[j]), resto[j + 1 :]
            return base, argv[1:]
        if argv[1] == "compose" and len(argv) >= 3 and argv[2] == "exec":
            resto = argv[3:]
            j = 0
            while j < len(resto) and resto[j].startswith("-"):
                j += 1
            if j < len(resto):
                j += 1  # nombre del servicio
            if j < len(resto):
                return os.path.basename(resto[j]), resto[j + 1 :]
            return base, argv[1:]
    return base, argv[1:]


def _git_add_bloquea(args: list[str]) -> str | None:
    for a in args:
        if a in ("-A", "--all", "."):
            return (
                "GUARDIÁN: 'git add -A/--all/.' prohibido (CLAUDE.md regla 4). "
                "Nombra los archivos: git add <ruta> ..."
            )
    for a in args:
        if a.startswith("-"):
            continue
        base = os.path.basename(a)
        if a.endswith((".xlsx", ".csv", ".dump", ".sql.gz")):
            return "GUARDIÁN: datos reales o secretos no van a git (CLAUDE.md regla 11)."
        if base == ".env" or (base.startswith(".env.") and not base.endswith(".example")):
            return "GUARDIÁN: datos reales o secretos no van a git (CLAUDE.md regla 11)."
    return None


PUSH_OK_RE = re.compile(r"^feature/T-\d+$")


def _git_push_bloquea(args: list[str]) -> str | None:
    permitido_flags = {"-u"}
    resto = []
    for a in args:
        if a in permitido_flags:
            continue
        resto.append(a)
    mensaje = (
        "GUARDIÁN: push solo 'git push [-u] origin feature/T-NNN', escrito solo, sin tuberías "
        "ni redirecciones (CLAUDE.md regla 4). El push de main lo hace " + LIDER + " desde su terminal."
    )
    if len(resto) != 2:
        return mensaje
    remoto, rama = resto
    if remoto != "origin":
        return mensaje
    if not PUSH_OK_RE.match(rama):
        return mensaje
    return None


def _destructivo_shell(programa: str, args: list[str]) -> bool:
    if programa in ("docker", "docker-compose"):
        resto = args
        if programa == "docker":
            if len(resto) < 2 or resto[0] != "compose" or resto[1] != "down":
                return False
            resto = resto[2:]
        else:
            if not resto or resto[0] != "down":
                return False
            resto = resto[1:]
        return any(a in ("-v", "--volumes") for a in resto)
    if programa == "alembic":
        return "downgrade" in args
    if programa == "rm":
        tiene_r = any(re.fullmatch(r"-r[f]*|-f[r]?|-[Rr][Ff]?", a) for a in args)
        tiene_ruta = any(("data/" in a or "pgdata" in a) for a in args)
        return tiene_r and tiene_ruta
    return False


def _hallar_arg_de_flag(args: list[str], flags: tuple[str, ...]) -> str | None:
    for i, a in enumerate(args):
        if a in flags and i + 1 < len(args):
            return args[i + 1]
    return None


def _indices_de_texto_inerte(argv: list[str], programa: str, resto: list[str]) -> set[int]:
    """Posiciones en argv cuyo contenido es texto inerte (no se le aplica ninguna regla,
    tampoco la autoprotección): valor de git commit -m/--message, argumentos de echo/printf."""
    if resto != argv[1:]:
        # resto viene de resolver un docker exec/compose exec: los índices no corresponden
        # 1:1 con argv. No se marca nada inerte (más conservador, no menos).
        return set()
    indices: set[int] = set()
    if programa == "git" and resto and resto[0] == "commit":
        for flag in ("-m", "--message"):
            if flag in resto:
                j = resto.index(flag)
                if j + 1 < len(resto):
                    indices.add(j + 2)
    if programa in ("echo", "printf"):
        indices.update(range(1, len(argv)))
    return indices


def _es_sql_destructivo(texto: str) -> bool:
    return bool(SQL_DESTRUCTIVE_RE.search(_collapse_ws(texto)))


EJECUTABLES_HEREDOC = {"psql", "bash", "sh", "python", "python3"}
INERTES_HEREDOC = {"cat", "tee"}


def _clasificar_heredoc(programa: str, args: list[str], cuerpo: str) -> str | None:
    """None = inerte/ok; mensaje si bloquea (DROP en texto ejecutable)."""
    if programa in INERTES_HEREDOC:
        return None
    if programa == "git" and "commit" in args:
        idx_f = None
        for flag in ("-F", "--file"):
            if flag in args:
                idx_f = args.index(flag)
                break
        if idx_f is not None and idx_f + 1 < len(args) and args[idx_f + 1] == "-":
            return None
    if programa in EJECUTABLES_HEREDOC:
        if _es_sql_destructivo(cuerpo):
            return "destructivo"
        return None
    return None


class Bloqueo(Exception):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


def analizar_comando_simple(
    argv_crudo: list[str],
    heredocs: dict[str, str],
    *,
    top_level: bool,
) -> Analysis:
    if any(t.startswith(("__HEREDOC_UNCLOSED__", "__SUBST_UNCLOSED__")) for t in argv_crudo):
        return Analysis(hard_block="GUARDIÁN: comando no interpretable (heredoc/sustitución sin cerrar). Falla cerrado.")

    argv, asignaciones = despojar_envoltorios(argv_crudo)
    if not argv:
        return Analysis()

    if os.path.basename(argv[0]) == "eval":
        return Analysis(hard_block="GUARDIÁN: 'eval' prohibido siempre (PROCESO.md §Guardián).")

    programa, resto = resolver_programa(argv)

    if not top_level and programa not in KNOWN_PROGRAMS:
        return Analysis(
            hard_block=(
                f"GUARDIÁN: comando no interpretable dentro de una sustitución/subshell "
                f"('{programa}' no es un programa reconocido). Falla cerrado (PROCESO.md §Guardián)."
            )
        )

    # Autoprotección: cualquier token que nombre una ruta protegida, salvo lectores seguros.
    # El valor de un argumento inerte (mensaje de commit, argumento de echo/printf) no cuenta:
    # "el cierre menciona .claude/" en un mensaje de commit no es tocar .claude/.
    indices_inertes = _indices_de_texto_inerte(argv, programa, resto)
    if programa not in SAFE_READERS and any(
        _is_protected_path(t) for i, t in enumerate(argv) if i not in indices_inertes
    ):
        return Analysis(
            hard_block=(
                "GUARDIÁN: autoprotección — no se toca .claude/ ni ~/." + PROYECTO_SLUG + "/ desde "
                "Claude Code (CLAUDE.md regla 7). Pide a " + LIDER + " que lo haga desde su terminal."
            )
        )

    analysis = Analysis()

    if programa == "git":
        sub = resto[0] if resto else ""
        if sub == "add":
            msg = _git_add_bloquea(resto[1:])
            if msg:
                return Analysis(hard_block=msg)
        elif sub == "merge":
            analysis.needs.add("MERGE_OK")
        elif sub == "push":
            msg = _git_push_bloquea(resto[1:])
            if msg:
                return Analysis(hard_block=msg)

    if _destructivo_shell(programa, resto):
        analysis.needs.add("DESTRUCTIVO_OK")

    if programa == "psql":
        arg_c = _hallar_arg_de_flag(resto, ("-c",))
        if arg_c is not None and _es_sql_destructivo(arg_c):
            analysis.needs.add("DESTRUCTIVO_OK")
        arg_f = _hallar_arg_de_flag(resto, ("-f",))
        if arg_f is not None:
            try:
                contenido = Path(arg_f).read_text()
            except OSError:
                return Analysis(hard_block=f"GUARDIÁN: no se pudo leer {arg_f} para revisarlo. Falla cerrado.")
            if _es_sql_destructivo(contenido):
                analysis.needs.add("DESTRUCTIVO_OK")

    if programa in ("bash", "sh"):
        arg_c = _hallar_arg_de_flag(resto, ("-c",))
        if arg_c is not None:
            sub_analysis = analizar_script(arg_c, top_level=False)
            analysis.merge(sub_analysis)
            if analysis.hard_block is not None:
                return analysis

    if programa == "make" and "instalar-guardian" in resto:
        dest = None
        for tok in list(asignaciones.items()):
            if tok[0] == "GUARDIAN_DEST":
                dest = tok[1]
        for a in resto:
            if a.startswith("GUARDIAN_DEST="):
                dest = a.split("=", 1)[1]
        if not dest or not dest.startswith("/tmp/"):
            return Analysis(
                hard_block=(
                    "GUARDIÁN: 'make instalar-guardian' solo con GUARDIAN_DEST= bajo /tmp/ "
                    "desde Claude Code (CLAUDE.md regla 7). " + LIDER + " lo instala en ~/." + PROYECTO_SLUG
                    + "/ desde su terminal."
                )
            )

    # heredocs asociados a este comando simple
    for marcador, cuerpo in heredocs.items():
        if marcador in argv_crudo:
            msg_clase = _clasificar_heredoc(programa, resto, cuerpo)
            if msg_clase == "destructivo":
                analysis.needs.add("DESTRUCTIVO_OK")

    return analysis


def analizar_script(texto: str, *, top_level: bool) -> Analysis:
    texto_sin_heredoc, heredocs = extraer_heredocs(texto)
    texto_sin_subs, subs = extraer_sustituciones(texto_sin_heredoc)

    analysis = Analysis()
    for contenido in subs.values():
        sub_analysis = analizar_script(contenido, top_level=False)
        analysis.merge(sub_analysis)
        if analysis.hard_block is not None:
            return analysis

    texto_para_tokenizar = texto_sin_subs.replace("\n", " ; ")
    tokens = tokenizar(texto_para_tokenizar)
    if tokens is None:
        return Analysis(hard_block="GUARDIÁN: comando no interpretable (tokenización falló). Falla cerrado.")

    for comando in partir_en_comandos_simples(tokens):
        resultado = analizar_comando_simple(comando, heredocs, top_level=top_level)
        analysis.merge(resultado)
        if analysis.hard_block is not None:
            return analysis

    return analysis


def decidir_y_consumir(analysis: Analysis, raiz: Path) -> tuple[bool, str]:
    if analysis.hard_block is not None:
        return False, analysis.hard_block
    if not analysis.needs:
        return True, ""
    faltantes = [f for f in analysis.needs if not (raiz / ".claude" / f).is_file()]
    if faltantes:
        return False, (
            f"GUARDIÁN: falta(n) bandera(s) {', '.join(sorted(faltantes))} para autorizar este paso "
            "(CLAUDE.md regla 7). Pide a " + LIDER + " que la(s) cree en esta conversación."
        )
    for f in analysis.needs:
        try:
            (raiz / ".claude" / f).unlink()
        except OSError:
            pass
    return True, ""


EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

ADR_RE = re.compile(r"(^|/)docs/adr/ADR-\d{3}-.*\.md$")
CIERRE_RE = re.compile(r"(^|/)docs/cierres/.*\.md$")
MAESTRO_RE = re.compile(r"(^|/)docs/(DATA_MODEL_|BUSINESS_RULES_|ARCHITECTURE_RULES_)")
# La BITACORA vigente y las sesiones fechadas las escribe el Project con el líder.
BITACORA_RE = re.compile(r"(^|/)docs/(BITACORA\.md$|bitacora/)")


def analizar_edicion(ruta: str, raiz: Path) -> Analysis:
    if _is_protected_path(ruta):
        return Analysis(
            hard_block=(
                "GUARDIÁN: autoprotección — no se edita .claude/ ni ~/." + PROYECTO_SLUG + "/ desde "
                "Claude Code (CLAUDE.md regla 7)."
            )
        )
    path = Path(ruta)
    if ADR_RE.search(ruta):
        if path.is_file():
            return Analysis(needs={"ADR_OK"})
        return Analysis()
    if CIERRE_RE.search(ruta):
        if path.is_file():
            return Analysis(needs={"MERGE_OK"})
        return Analysis()
    if MAESTRO_RE.search(ruta):
        return Analysis(
            hard_block=(
                "GUARDIÁN: los documentos maestros se reversionan desde el Project, no desde "
                "Claude Code. Reporta la discrepancia en el cierre."
            )
        )
    if BITACORA_RE.search(ruta):
        return Analysis(
            hard_block=(
                "GUARDIÁN: la BITACORA y docs/bitacora/ las mantiene el Project con " + LIDER
                + ". Lo que quieras registrar va al cierre de la tarea."
            )
        )
    return Analysis()


def main() -> int:
    raiz_str = os.environ.get("CLAUDE_PROJECT_DIR")
    if not raiz_str:
        sys.stderr.write("GUARDIÁN: falta CLAUDE_PROJECT_DIR. Falla cerrado.\n")
        return 2
    raiz = Path(raiz_str)

    try:
        entrada = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.stderr.write("GUARDIÁN: entrada JSON ilegible. Falla cerrado.\n")
        return 2

    if not isinstance(entrada, dict):
        sys.stderr.write("GUARDIÁN: entrada JSON ilegible. Falla cerrado.\n")
        return 2

    tool_name = entrada.get("tool_name")
    tool_input = entrada.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    if tool_name == "Bash":
        comando = tool_input.get("command")
        if not isinstance(comando, str):
            sys.stderr.write("GUARDIÁN: comando Bash sin texto. Falla cerrado.\n")
            return 2
        try:
            analysis = analizar_script(comando, top_level=True)
        except RecursionError:
            sys.stderr.write("GUARDIÁN: comando demasiado anidado. Falla cerrado.\n")
            return 2
        permite, mensaje = decidir_y_consumir(analysis, raiz)
    elif tool_name in EDIT_TOOLS:
        ruta = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("notebook_path")
        if not isinstance(ruta, str):
            sys.stderr.write("GUARDIÁN: edición sin ruta. Falla cerrado.\n")
            return 2
        analysis = analizar_edicion(ruta, raiz)
        permite, mensaje = decidir_y_consumir(analysis, raiz)
    else:
        sys.stderr.write(f"GUARDIÁN: herramienta no reconocida '{tool_name}'. Falla cerrado.\n")
        return 2

    if not permite:
        sys.stderr.write(mensaje + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
