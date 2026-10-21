# Cierre de sesión — Fabricante de Ideas

Sin Claude Code ni worktree: los commits se hacen en `~/proyectos/FabricanteDeIdeas`.

## 1. Lo que entrega el Project
Archivos completos, como descargables: la sesión nueva `AAMMDD_sesion.md` (`docs/bitacora/`; segunda
del día: `AAMMDD_2_sesion.md`) con el hash del cierre anterior, la `BITACORA.md` (`docs/`) y lo que
cambió (`docs/PROYECTOS.md`, archivos del kit en `kit/…`, las instrucciones). Si son más de tres
archivos, un solo zip con las rutas del repo, que se extrae sobre el repo.

## 2. Pasos de Tomek
**1. Descargar** todo a `D:\Descargas\FabricanteDeIdeas`.

**2. Poner el repo al día (terminal SSH)**
```bash
ssh orangepi@192.168.1.163
cd ~/proyectos/FabricanteDeIdeas
git pull
git log --oneline -1
```

**3. Copiar (PowerShell)**, una línea por archivo, con la ruta de destino que dé el Project:
```powershell
scp D:\Descargas\FabricanteDeIdeas\BITACORA.md orangepi@192.168.1.163:~/proyectos/FabricanteDeIdeas/docs/BITACORA.md
scp D:\Descargas\FabricanteDeIdeas\AAMMDD_sesion.md orangepi@192.168.1.163:~/proyectos/FabricanteDeIdeas/docs/bitacora/
```
Con zip: `scp` del zip a `~/` y, en el Pi, `python3 -m zipfile -e ~/<zip> .` dentro del repo.

**4. Commit y push (terminal SSH)**
```bash
cd ~/proyectos/FabricanteDeIdeas
git status -sb                      # solo los archivos entregados
git add docs/BITACORA.md docs/bitacora/AAMMDD_sesion.md
git commit -m "Cierre AAAA-MM-DD: <tema>"
git push origin main
git log --oneline -1                # anota el hash: el Project lo pide en la sesión siguiente
```

**5. «Sync now» (siempre el último):** Knowledge del Project → fuente de GitHub
`tdkgo2/FabricanteDeIdeas` → **Sync now**. No se sube nada a mano. Si cambiaron las instrucciones,
se vuelven a pegar antes.
