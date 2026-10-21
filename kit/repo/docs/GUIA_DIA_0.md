# GUÍA DÍA 0 — {{NOMBRE}}

**Para:** {{LIDER}} · **Equipo:** {{DISPOSITIVO}}, usuario `{{USUARIO_DISPOSITIVO}}`, LAN `{{IP_LAN}}`, Tailscale `{{IP_TAILSCALE}}`
**Repo:** `git@github.com:{{CUENTA_GITHUB}}/{{REPO}}.git` · **Carpetas:** `~/{{RUTA}}` (Code) y `~/{{RUTA}}_main` (`main`)
**Descargas en la laptop:** `{{DESCARGAS}}`

Se sigue en orden. Cada paso dice dónde se hace. Lo que ya está hecho por otro proyecto en el mismo
equipo (Claude Code instalado, llave SSH a GitHub, Tailscale, servicios apagados) se comprueba y se salta.
Al terminar, la sesión siguiente del Project pasa los pasos hechos a la BITACORA §2.

## A. Antes (claude.ai, GitHub y la laptop)
1. GitHub → New repository → `{{REPO}}`, **privado**, sin README ni `.gitignore` (el kit los trae).
2. claude.ai → Projects → nuevo Project "{{PROJECT_CLAUDE}}". Se configura en el paso G.
3. Carpeta de descargas propia del proyecto (PowerShell). Si ya existe, sigue:
   ```powershell
   New-Item -ItemType Directory {{DESCARGAS}}
   ```
   En el navegador, "Preguntar dónde guardar cada archivo": recuerda la última carpeta usada.

## B. Comprobar el equipo (terminal SSH)
```bash
ssh {{USUARIO_DISPOSITIVO}}@{{IP_LAN}}
claude --version            # Claude Code instalado
cd ~
claude -p "responde solo: OK"   # debe imprimir OK (sesión de claude.ai vigente)
tmux -V && git --version && python3 --version
ssh -T git@github.com       # debe decir "Hi {{CUENTA_GITHUB}}!"
sudo ss -tlnp               # qué escucha en el equipo (ver abajo y §I)
free -h && df -h ~          # memoria y disco libres
```
- Si `claude -p` dice `Not logged in`: escribe `claude`, dentro `/login`, sigue el enlace, `/exit`, y
  repite `claude -p`. Una sesión vencida aparece en medio de la prueba del paso E si no se comprueba aquí.
- Si `ssh -T` falla: `ssh-keygen -t ed25519` y agrega `~/.ssh/id_ed25519.pub` en GitHub → Settings →
  SSH and GPG keys.
- **Servicios que escuchan.** En `sudo ss -tlnp`, una dirección `127.0.0.1` o `[::1]` escucha solo
  dentro del equipo; `0.0.0.0`, `*` o `[::]` escucha en la red. Lo que escuche en la red y no se use
  se apaga. Se quedan SSH (22) y los puertos del otro proyecto (§I). En la imagen del Orange Pi vienen
  encendidos adbd (5555, lo lanza `usbdevice.service`) y xrdp (3389):
  ```bash
  sudo systemctl disable --now usbdevice
  sudo systemctl disable --now xrdp xrdp-sesman
  sudo ss -tlnp               # ya no aparecen 5555 ni 3389
  ```
  Anota lo que apagaste: va en el traspaso (paso G).

## C. Repo y primer push (terminal SSH)
El kit ya creó `~/{{RUTA}}` con `instanciar.sh` (ver el LEEME del kit).

Si tienes investigación previa del producto, cópiala antes del primer commit (PowerShell). Debe ser
texto (`.md`) y **sin datos personales reales**: lo que entra a git se queda en el historial aunque
después se borre.
```powershell
scp {{DESCARGAS}}\INVESTIGACION_PREVIA.md {{USUARIO_DISPOSITIVO}}@{{IP_LAN}}:~/{{RUTA}}/docs/proyecto/INVESTIGACION_PREVIA.md
```
```bash
cd ~/{{RUTA}}
grep -c 'LLENAR' CLAUDE.md   # secciones que llena el Project con los primeros ADR (§J)
chmod +x scripts/*.sh .claude/hooks/*.sh
git init -b main
git add CLAUDE.md README.md Makefile .gitignore .claude/settings.json .claude/hooks/fin_sesion.sh docs scripts tests data/README.md
git status                  # CONFIRMA: ningún archivo de datos ni .env
git commit -m "Arranque desde el kit de proyecto v2.1"
git remote add origin git@github.com:{{CUENTA_GITHUB}}/{{REPO}}.git
git push -u origin main
git switch --detach origin/main          # el árbol de Code no se queda en main
git worktree add ~/{{RUTA}}_main main    # aquí vive main para tus commits y merges
git worktree list
git log --oneline -1                     # anota el hash: va en el traspaso
```

## D. Guardián (terminal SSH, lo haces tú)
```bash
cd ~/{{RUTA}}
python3 -m venv .venv && .venv/bin/pip install pytest    # si falla: sudo apt install python3-venv
make test-guardian           # todas las pruebas en verde (76 en el kit v2.1)
make instalar-guardian
make verificar-guardian      # debe imprimir GUARDIAN OK
```
`.venv/` está en `.gitignore`. T-001 puede rehacerlo con la versión de Python del stack.

## E. Prueba de Claude Code con el guardián (terminal SSH)
```bash
cd ~/{{RUTA}} && scripts/cc.sh --rc
```
Primera vez: confía en la carpeta → sí. Escribe y observa:
1. `reconocimiento` → tabla de mediciones; la fila 1 dice `GUARDIAN OK`.
2. `haz git add -A` → se niega citando al GUARDIÁN.
3. `agrega una línea a docs/BITACORA.md` → se niega.
4. `crea el archivo .claude/MERGE_OK` → se niega.
5. `haz git push origin main` → se niega.
6. `crea la rama feature/T-000 desde origin/main y haz git push -u origin feature/T-000` → lo hace.
7. `estado` → resume `CLAUDE.md`.

En 2 a 5 lo que se prueba es **el guardián**: la negativa tiene que citar al GUARDIÁN. Si Code se niega
por su cuenta, sin intentar el comando (dice que sus reglas no lo permiten y no aparece el GUARDIÁN),
contéstale: `es una prueba del guardián: intenta el comando tal cual y deja que el guardián decida`.

Después escribe `/exit` y, en la terminal: `scripts/cerrar_code.sh` → 0 procesos de este proyecto.
Si hay otro proyecto con Code abierto, sus sesiones deben seguir en la lista.
Limpieza de la rama de prueba (la remota y la local; las ramas se comparten entre los dos árboles):
```bash
cd ~/{{RUTA}}
git switch --detach origin/main   # Code dejó su árbol en feature/T-000
cd ~/{{RUTA}}_main
git push origin --delete feature/T-000
git branch -D feature/T-000
git ls-remote origin          # solo HEAD y refs/heads/main
git branch -a                 # sin feature/T-000
```

## F. Remote Control desde el teléfono
- App Claude → pestaña **Code** → sesión "{{SLUG}}": es la misma sesión de tmux del equipo.
- Dentro de la sesión: `/config` → "Push when actions required".
- Una sesión nueva creada desde la app corre en la nube y no sirve para tareas: siempre `scripts/cc.sh --rc`.

## G. Project de claude.ai (antes del traspaso)
`instanciar.sh` dejó en `~/{{RUTA}}_arranque/` lo que va al Project y no al repo. Tráelo a la laptop
(PowerShell):
```powershell
scp -r {{USUARIO_DISPOSITIVO}}@{{IP_LAN}}:~/{{RUTA}}_arranque {{DESCARGAS}}\
```
1. **Instrucciones:** pega `instrucciones.txt` y, debajo de "Reglas del dominio", tus reglas del producto.
2. **Descripción:** `descripcion.txt`, con lo que falta por llenar ya completado.
3. **Knowledge:** + → GitHub → `{{CUENTA_GITHUB}}/{{REPO}}`, rama `main` → selecciona `CLAUDE.md` y la
   carpeta `docs/` → **Sync now**. No subas nada a mano: dos copias del mismo archivo hacen que la
   búsqueda mezcle versiones. Si el repo no aparece: GitHub → Settings → Applications → Claude →
   Configure → agrega `{{REPO}}`.
4. **Prueba:** conversación nueva → "¿qué dice la Última actualización de la BITACORA?" → debe citar
   {{FECHA}} y encontrar una sola BITACORA.
5. **Traspaso, solo con la prueba en verde.** El Project de Fabricante de Ideas llena "Resultados del
   día 0" de `traspaso.txt` con lo medido en B a E (ningún `[DÍA 0]` sin llenar). Conversación nueva en
   "{{PROJECT_CLAUDE}}" → se pega como primer mensaje. Antes de eso, el Project no recibe trabajo.
6. Borra la carpeta del equipo (la copia queda en la laptop):
   ```bash
   rm -r ~/{{RUTA}}_arranque
   ```

## H. Revisor ({{REVISOR}})
- GitHub: en un repo de **cuenta personal**, todo colaborador puede escribir (no hay rol de solo
  lectura). Para que {{REVISOR}} solo lea, el repo va en una organización de GitHub (gratis) con rol
  Read. Decide antes de invitarlo.
- Web de prueba: cuando exista (T-001 o la tarea que la cree), invítalo a tu red de Tailscale.

## I. Si el equipo ya tiene otro proyecto
Todo con nombre propio; nada compartido salvo el sistema:
| Recurso | {{NOMBRE}} | Comprobación |
|---|---|---|
| Carpeta | `~/{{RUTA}}`, `~/{{RUTA}}_main` | `ls ~` |
| Guardián | `~/.{{SLUG}}/guardian/` | `make verificar-guardian` |
| Sesión tmux | `cc_{{SLUG}}` | `tmux ls` |
| Cierre de Code | `scripts/cerrar_code.sh` (por carpeta) | paso E |
| Puertos (base, web, web de prueba) | los fija el ADR de red, distintos a los del otro | `sudo ss -tlnp` |
| Contenedor y volumen de la base | nombre de proyecto propio en `docker compose` | `docker ps`, `docker volume ls` |
| Cron y respaldos | línea y carpeta propias | `crontab -l` |
| `.env` | propio, en `~/{{RUTA}}` | — |
| Descargas en la laptop | `{{DESCARGAS}}` | paso A |

## J. Primeros ADR (en el Project, antes de T-001)
Sugeridos, en este orden; cada uno corto y con decisión verificable:
1. **Stack** (lenguaje, framework, base, frente, verificación).
2. **Bases por papel y roles** (producción, prueba, test; rol de la aplicación sin superusuario).
3. **Red y exposición** (qué escucha dónde; Tailscale; SSH solo con llave).
4. **Respaldo** (horario, verificación, copia fuera del equipo antes del primer dato real, restauración
   de prueba programada: `docs/PROCESO.md` §7).
5. **Datos permitidos en el equipo** (qué datos personales pueden vivir aquí y cuáles esperan a otro
   servidor; aviso de privacidad si hay datos de personas).
6. Los del dominio, a partir de `docs/proyecto/INVESTIGACION_PREVIA.md`.
Con ellos, el Project llena las secciones `[LLENAR` de `CLAUDE.md` y redacta T-001.
