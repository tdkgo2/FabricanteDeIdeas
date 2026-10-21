"""Guardián v2 del kit (origen: T-009 / ADR-047 de Trama). Cada caso corre el guardián vía
subprocess con /usr/bin/python3, en un .claude/ de tmp_path — nunca contra el real."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

GUARDIAN_SRC = Path(__file__).resolve().parents[1] / "scripts" / "guardian" / "guardian.py"
PYTHON310 = "/usr/bin/python3"


@pytest.fixture()
def sandbox(tmp_path: Path) -> Path:
    (tmp_path / ".claude").mkdir()
    shutil.copy(GUARDIAN_SRC, tmp_path / "guardian.py")
    return tmp_path


def correr(
    sandbox: Path,
    payload: dict[str, object] | str,
    banderas_previas: set[str] = frozenset(),  # type: ignore[assignment]
    *,
    sin_project_dir: bool = False,
) -> tuple[int, str, set[str]]:
    for f in (sandbox / ".claude").glob("*_OK"):
        f.unlink()
    for nombre in banderas_previas:
        (sandbox / ".claude" / nombre).touch()
    entrada = json.dumps(payload) if isinstance(payload, dict) else payload
    env_completo = dict(os.environ)
    if sin_project_dir:
        env_completo.pop("CLAUDE_PROJECT_DIR", None)
    else:
        env_completo["CLAUDE_PROJECT_DIR"] = str(sandbox)
    proc = subprocess.run(
        [PYTHON310, str(sandbox / "guardian.py")],
        input=entrada,
        text=True,
        cwd=str(sandbox),
        env=env_completo,
        capture_output=True,
        check=False,
    )
    banderas_despues = {p.name for p in (sandbox / ".claude").glob("*_OK")}
    return proc.returncode, proc.stderr, banderas_despues


def bash(comando: str) -> dict[str, object]:
    return {"tool_name": "Bash", "tool_input": {"command": comando}}


def edit(ruta: str, tool: str = "Edit") -> dict[str, object]:
    return {"tool_name": tool, "tool_input": {"file_path": ruta}}


# ---------------------------------------------------------------------------
# Matriz de FASE 2 de la tarea T-009.
# ---------------------------------------------------------------------------


def test_merge_sin_bandera_bloquea(sandbox: Path) -> None:
    code, _err, flags = correr(sandbox, bash('git merge --no-ff feature/T-006 -m "T-006: merge"'))
    assert code == 2
    assert flags == set()


def test_merge_con_bandera_permite_y_consume(sandbox: Path) -> None:
    code, _err, flags = correr(
        sandbox, bash('git merge --no-ff feature/T-006 -m "T-006: merge"'), {"MERGE_OK"}
    )
    assert code == 0
    assert flags == set()


def test_merge_con_cd_previo_consume(sandbox: Path) -> None:
    code, _err, flags = correr(
        sandbox, bash("cd ~/{{RUTA}} && git merge --no-ff feature/T-006"), {"MERGE_OK"}
    )
    assert code == 0
    assert flags == set()


def test_dos_merges_consumen_una_sola_vez(sandbox: Path) -> None:
    code, _err, flags = correr(sandbox, bash("git merge a && git merge b"), {"MERGE_OK"})
    assert code == 0
    assert flags == set()


def test_heredoc_a_cat_con_texto_peligroso_es_inerte(sandbox: Path) -> None:
    comando = "cat > notas.md <<'EOF'\ngit merge y DROP DATABASE son solo texto\nEOF"
    code, _err, flags = correr(sandbox, bash(comando), {"MERGE_OK"})
    assert code == 0
    assert flags == {"MERGE_OK"}


def test_commit_con_texto_peligroso_en_mensaje_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(
        sandbox, bash('git commit -m "menciona .env.example y DROP DATABASE"')
    )
    assert code == 0


def test_add_env_example_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("git add .env.example"))
    assert code == 0


@pytest.mark.parametrize(
    "comando",
    [
        "git add .env",
        "git add .env.local",
        "git add data/x.xlsx",
        "git add -A",
        "git add .",
    ],
)
def test_add_prohibido_bloquea(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 2


@pytest.mark.parametrize(
    "comando",
    [
        'psql -c "DROP DATABASE x;"',
        'docker compose exec db psql -c "drop  database x"',
    ],
)
def test_psql_c_destructivo_bloquea(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 2


def test_psql_heredoc_destructivo_bloquea(sandbox: Path) -> None:
    comando = "psql <<'EOF'\nDROP DATABASE x;\nEOF"
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 2


def test_psql_f_archivo_destructivo_bloquea(sandbox: Path, tmp_path: Path) -> None:
    (tmp_path / "borrar.sql").write_text("DROP TABLE rollos;\n")
    code, _err, _flags = correr(sandbox, bash("psql -f borrar.sql"))
    assert code == 2


def test_psql_f_archivo_inexistente_falla_cerrado(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("psql -f no_existe_12345.sql"))
    assert code == 2


def test_bash_c_con_merge_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash('bash -c "git merge x"'))
    assert code == 2


def test_sustitucion_con_programa_no_reconocido_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("echo $(dropdb x)"))
    assert code == 2


def test_eval_bloquea_siempre(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash('eval "ls"'))
    assert code == 2


@pytest.mark.parametrize(
    "comando",
    ["git push origin feature/T-009", "git push -u origin feature/T-009"],
)
def test_push_feature_forma_correcta_permite(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 0


@pytest.mark.parametrize(
    "comando",
    ["git push", "git push origin main", "git push -f origin feature/T-009"],
)
def test_push_forma_incorrecta_bloquea_bandera_intacta(sandbox: Path, comando: str) -> None:
    code, _err, flags = correr(sandbox, bash(comando), {"MERGE_OK"})
    assert code == 2
    assert flags == {"MERGE_OK"}


@pytest.mark.parametrize(
    "comando",
    [
        "touch .claude/MERGE_OK",
        "rm .claude/MERGE_OK",
        "chmod 777 .claude",
        "> .claude/ADR_OK",
    ],
)
def test_autoproteccion_bash_bloquea(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 2


@pytest.mark.parametrize(
    "comando",
    ["ls -la .claude/", "sha256sum ~/.{{SLUG}}/guardian/guardian.py"],
)
def test_autoproteccion_lectores_seguros_permite(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 0


def test_ejecutar_guardian_a_mano_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("/usr/bin/python3 ~/.{{SLUG}}/guardian/guardian.py"))
    assert code == 2


def test_edit_settings_json_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, edit(".claude/settings.json"))
    assert code == 2


def test_edit_bitacora_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, edit("docs/BITACORA.md"))
    assert code == 2


def test_edit_adr_existente_sin_bandera_bloquea(sandbox: Path) -> None:
    ruta = sandbox / "docs" / "adr" / "ADR-047-guardian-fuera-del-arbol.md"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("x")
    code, _err, _flags = correr(sandbox, edit(str(ruta.relative_to(sandbox))))
    assert code == 2


def test_edit_adr_existente_con_bandera_permite_y_consume(sandbox: Path) -> None:
    ruta = sandbox / "docs" / "adr" / "ADR-047-guardian-fuera-del-arbol.md"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("x")
    code, _err, flags = correr(
        sandbox, edit(str(ruta.relative_to(sandbox))), {"ADR_OK"}
    )
    assert code == 0
    assert flags == set()


def test_edit_cierre_nuevo_sin_bandera_permite(sandbox: Path) -> None:
    # El archivo todavía no existe: no es "write-once" hasta que se crea.
    code, _err, _flags = correr(sandbox, edit("docs/cierres/T-009_2026-10-03.md"))
    assert code == 0


def test_edit_cierre_existente_sin_bandera_bloquea(sandbox: Path) -> None:
    ruta = sandbox / "docs" / "cierres" / "T-005_2026-10-01.md"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("x")
    code, _err, _flags = correr(sandbox, edit(str(ruta.relative_to(sandbox))))
    assert code == 2


def test_edit_seccion_merge_de_cierre_existente_permite_y_consume(sandbox: Path) -> None:
    ruta = sandbox / "docs" / "cierres" / "T-005_2026-10-01.md"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("x")
    code, _err, flags = correr(
        sandbox, edit(str(ruta.relative_to(sandbox))), {"MERGE_OK"}
    )
    assert code == 0
    assert flags == set()


def test_comando_que_necesita_dos_banderas_con_solo_una_bloquea_ninguna_borrada(
    sandbox: Path,
) -> None:
    code, _err, flags = correr(sandbox, bash("git merge a && rm -rf data/foo"), {"MERGE_OK"})
    assert code == 2
    assert flags == {"MERGE_OK"}


def test_json_roto_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, "{esto no es json")
    assert code == 2


def test_sin_claude_project_dir_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("ls"), sin_project_dir=True)
    assert code == 2


# ---------------------------------------------------------------------------
# Los tres payloads reales del incidente del 03-10 (FASE 1.2 del cierre).
# ---------------------------------------------------------------------------


def test_incidente_merge_ffonly_sincronizacion_consume_de_mas(sandbox: Path) -> None:
    """El guardián v2 también consume MERGE_OK con un --ff-only de sincronización:
    sigue sin distinguir qué merge autorizó el líder (límite conocido, ver cierre §4)."""
    code, _err, flags = correr(
        sandbox, bash("git checkout main && git merge --ff-only origin/main"), {"MERGE_OK"}
    )
    assert code == 0
    assert flags == set()


def test_incidente_merge_real_de_t006_consume(sandbox: Path) -> None:
    comando = (
        'git merge --no-ff feature/T-006 -m '
        '"Merge feature/T-006: produccion y archivo en solo lectura (ADR-046)"'
    )
    code, _err, flags = correr(sandbox, bash(comando), {"MERGE_OK"})
    assert code == 0
    assert flags == set()


def test_incidente_edicion_seccion_merge_del_cierre_t006_consume(sandbox: Path) -> None:
    ruta = sandbox / "docs" / "cierres" / "T-006_2026-10-02.md"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("# T-006\n")
    code, _err, flags = correr(sandbox, edit(str(ruta.relative_to(sandbox))), {"MERGE_OK"})
    assert code == 0
    assert flags == set()


# ---------------------------------------------------------------------------
# Una prueba por cada regla de guardian.sh (FASE 0 f) no cubierta arriba:
# un caso que bloquea y uno parecido que no.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando,bandera,code,flags_despues",
    [
        ("docker compose down -v", frozenset(), 2, frozenset()),
        ("docker compose down -v", frozenset({"DESTRUCTIVO_OK"}), 0, frozenset()),
        ("docker compose down", frozenset(), 0, frozenset()),
        ("alembic downgrade -1", frozenset({"DESTRUCTIVO_OK"}), 0, frozenset()),
        ("alembic upgrade head", frozenset(), 0, frozenset()),
        ("rm -rf data/foo", frozenset({"DESTRUCTIVO_OK"}), 0, frozenset()),
        ("rm -rf /tmp/algo", frozenset(), 0, frozenset()),
    ],
)
def test_destructivos_pares_bloquea_permite(
    sandbox: Path, comando: str, bandera: frozenset[str], code: int, flags_despues: frozenset[str]
) -> None:
    obtenido_code, _err, obtenido_flags = correr(sandbox, bash(comando), set(bandera))
    assert obtenido_code == code
    assert obtenido_flags == set(flags_despues)


def test_master_doc_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, edit("docs/DATA_MODEL_v2_4.md"))
    assert code == 2


def test_doc_normal_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, edit("docs/tareas/T-010_siguiente.md"))
    assert code == 0


def test_git_status_normal_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("git status -sb"))
    assert code == 0


def test_pytest_normal_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("pytest -q"))
    assert code == 0


def test_checkout_de_ruta_protegida_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("git checkout -- .claude/hooks/guardian.sh"))
    assert code == 2


def test_write_sobre_home_del_guardian_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(
        sandbox, edit("/home/{{USUARIO_DISPOSITIVO}}/.{{SLUG}}/guardian/guardian.py", tool="Write")
    )
    assert code == 2


def test_make_instalar_guardian_sin_tmp_bloquea(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("make instalar-guardian"))
    assert code == 2


def test_make_instalar_guardian_con_tmp_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash("make instalar-guardian GUARDIAN_DEST=/tmp/xyz"))
    assert code == 0


def test_echo_texto_con_palabras_peligrosas_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash('echo "DROP DATABASE es solo texto"'))
    assert code == 0


def test_commit_mensaje_que_menciona_claude_permite(sandbox: Path) -> None:
    # Bug real encontrado al comitear T-009: el valor de -m es texto inerte
    # (CLAUDE.md regla), igual que ya lo es para los patrones destructivos.
    code, _err, _flags = correr(
        sandbox, bash('git commit -m "T-009: autoprotección sobre .claude/ y ~/.{{SLUG}}/"')
    )
    assert code == 0


def test_echo_que_menciona_home_del_guardian_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, bash('echo "instala el guardián en ~/.{{SLUG}}/guardian/"'))
    assert code == 0




# --- Kit: falsos positivos de Trama resueltos y BITACORA partida en sesiones ---


@pytest.mark.parametrize(
    "comando", ["git add .env.example", "git add .env.prueba.example", "git add docs/x.md"]
)
def test_add_plantillas_env_permite(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 0


@pytest.mark.parametrize("comando", ["git add .env.prueba", "git add data/a.csv"])
def test_add_secretos_y_datos_bloquea(sandbox: Path, comando: str) -> None:
    code, _err, _flags = correr(sandbox, bash(comando))
    assert code == 2


def test_plan_en_home_claude_plans_permite(sandbox: Path) -> None:
    code, _err, _flags = correr(sandbox, edit("~/.claude/plans/plan-t001.md", tool="Write"))
    assert code == 0
    ruta = str(Path.home() / ".claude" / "plans" / "plan-t001.md")
    code, _err, _flags = correr(sandbox, edit(ruta, tool="Write"))
    assert code == 0


@pytest.mark.parametrize(
    "ruta",
    ["~/.claude/plans/../settings.json", "~/.claude/settings.json", ".claude/settings.json"],
)
def test_resto_de_claude_sigue_protegido(sandbox: Path, ruta: str) -> None:
    code, _err, _flags = correr(sandbox, edit(ruta, tool="Write"))
    assert code == 2


@pytest.mark.parametrize(
    "ruta", ["docs/BITACORA.md", "docs/bitacora/261021_sesion.md", "docs/bitacora/LEEME.md"]
)
def test_bitacora_y_sesiones_bloquean(sandbox: Path, ruta: str) -> None:
    code, err, _flags = correr(sandbox, edit(ruta, tool="Write"))
    assert code == 2
    assert "BITACORA" in err


def test_mensaje_de_push_nombra_al_lider(sandbox: Path) -> None:
    code, err, _flags = correr(sandbox, bash("git push origin main"))
    assert code == 2
    assert "{{LIDER}}" in err
